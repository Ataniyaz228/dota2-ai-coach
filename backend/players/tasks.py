import logging
from datetime import datetime, timezone

from celery import shared_task
from django.db import transaction

from players.models import Player
from players.services import OpenDotaClient
from matches.models import (
    Hero, Match, PlayerMatch, MatchDraft, HeroBenchmark, PlayerHeroStats,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_player_data(self, account_id):
    """Full sync pipeline: profile → match list → match details → aggregates."""
    client = OpenDotaClient()

    try:
        player = Player.objects.get(account_id=account_id)
        player.sync_status = Player.SyncStatus.SYNCING
        player.save(update_fields=['sync_status'])

        # Phase 1: Profile
        _sync_profile(client, player)

        # Phase 2: Match list + details
        _sync_matches(client, player)

        # Phase 3: Aggregate hero stats
        _update_hero_stats(client, player)

        # Done
        player.sync_status = Player.SyncStatus.READY
        player.last_synced_at = datetime.now(timezone.utc)
        player.save(update_fields=['sync_status', 'last_synced_at'])

        logger.info(f'Successfully synced player {account_id}')

    except Player.DoesNotExist:
        logger.error(f'Player {account_id} not found in DB')
    except Exception as exc:
        logger.error(f'Sync failed for {account_id}: {exc}')
        try:
            player = Player.objects.get(account_id=account_id)
            player.sync_status = Player.SyncStatus.ERROR
            player.save(update_fields=['sync_status'])
        except Player.DoesNotExist:
            pass
        raise self.retry(exc=exc)


@shared_task
def sync_heroes():
    """Sync hero reference data from OpenDota."""
    client = OpenDotaClient()
    heroes_data = client.get_heroes()

    for h in heroes_data:
        Hero.objects.update_or_create(
            id=h['id'],
            defaults={
                'name': h.get('name', ''),
                'localized_name': h.get('localized_name', ''),
                'primary_attr': h.get('primary_attr', ''),
                'attack_type': h.get('attack_type', ''),
                'roles': h.get('roles', []),
                'img_url': f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{h.get('name', '').replace('npc_dota_hero_', '')}.png",
            }
        )

    logger.info(f'Synced {len(heroes_data)} heroes')


@shared_task
def sync_hero_benchmarks(hero_id):
    """Sync benchmark percentiles for a hero."""
    client = OpenDotaClient()

    try:
        hero = Hero.objects.get(id=hero_id)
    except Hero.DoesNotExist:
        logger.error(f'Hero {hero_id} not found')
        return

    data = client.get_hero_benchmarks(hero_id)
    result = data.get('result', {})

    for metric_name, percentile_data in result.items():
        HeroBenchmark.objects.update_or_create(
            hero=hero,
            metric=metric_name,
            defaults={'percentiles': percentile_data},
        )

    logger.info(f'Synced benchmarks for hero {hero.localized_name}')


@shared_task
def sync_all_benchmarks():
    """Sync benchmarks for all heroes in the DB."""
    hero_ids = Hero.objects.values_list('id', flat=True)
    for hero_id in hero_ids:
        sync_hero_benchmarks.delay(hero_id)


# =============================================================================
# Internal helpers
# =============================================================================

def _sync_profile(client, player):
    """Fetch and update player profile data."""
    data = client.get_player(player.account_id)
    profile = data.get('profile', {})

    player.personaname = profile.get('personaname', '') or ''
    player.avatar_url = profile.get('avatarfull', '') or ''
    player.steam_id_64 = int(profile.get('steamid', 0)) if profile.get('steamid') else None
    player.rank_tier = data.get('rank_tier')
    player.leaderboard_rank = data.get('leaderboard_rank')
    player.estimated_mmr = data.get('computed_mmr')

    # Fetch total lifetime win/loss
    try:
        wl_data = client.get_player_wl(player.account_id)
        wins = wl_data.get('win', 0)
        losses = wl_data.get('lose', 0)
        player.lifetime_wins = wins
        player.lifetime_matches = wins + losses
    except Exception as e:
        logger.warning(f"Failed to fetch wl for {player.account_id}: {e}")

    player.save(update_fields=[
        'personaname', 'avatar_url', 'steam_id_64',
        'rank_tier', 'leaderboard_rank', 'estimated_mmr',
        'lifetime_wins', 'lifetime_matches',
    ])

    # Trigger refresh on OpenDota to ensure latest data
    client.refresh_player(player.account_id)

    logger.info(f'Profile synced: {player.personaname} ({player.rank_display})')


def _sync_matches(client, player):
    """Fetch match list, then fetch detailed data for each match."""
    # Fetch match list (recent 50)
    matches_list = client.get_player_matches(player.account_id, limit=50)

    if not matches_list:
        logger.info(f'No matches found for {player.account_id}')
        return

    # Filter to matches we haven't synced yet
    if player.last_synced_match_id:
        matches_list = [
            m for m in matches_list
            if m['match_id'] > player.last_synced_match_id
        ]

    if not matches_list:
        logger.info(f'No new matches for {player.account_id}')
        return

    logger.info(f'Fetching details for {len(matches_list)} matches...')
    max_match_id = player.last_synced_match_id or 0

    for match_summary in matches_list:
        match_id = match_summary['match_id']
        max_match_id = max(max_match_id, match_id)

        # Skip if already have detailed data
        if Match.objects.filter(match_id=match_id).exists():
            # Still need to create PlayerMatch association if missing
            _ensure_player_match(player, match_id, match_summary)
            continue

        try:
            match_detail = client.get_match(match_id)
            _save_match_detail(match_detail, player)
        except Exception as e:
            logger.error(f'Failed to fetch match {match_id}: {e}')
            continue

    # Update last synced match ID
    player.last_synced_match_id = max_match_id
    player.save(update_fields=['last_synced_match_id'])


def _save_match_detail(data, player):
    """Parse and save full match data from OpenDota API response."""
    match_id = data['match_id']

    with transaction.atomic():
        # Create/update Match
        match, _ = Match.objects.update_or_create(
            match_id=match_id,
            defaults={
                'duration_seconds': data.get('duration', 0),
                'game_mode': data.get('game_mode', 0),
                'lobby_type': data.get('lobby_type', 0),
                'cluster': data.get('cluster'),
                'radiant_score': data.get('radiant_score', 0),
                'dire_score': data.get('dire_score', 0),
                'radiant_win': data.get('radiant_win'),
                'first_blood_time': data.get('first_blood_time'),
                'patch': data.get('patch'),
                'radiant_gold_adv': data.get('radiant_gold_adv'),
                'radiant_xp_adv': data.get('radiant_xp_adv'),
                'start_time': datetime.fromtimestamp(
                    data.get('start_time', 0), tz=timezone.utc
                ),
            }
        )

        # Save draft picks/bans
        picks_bans = data.get('picks_bans') or []
        for pb in picks_bans:
            hero_id = pb.get('hero_id')
            if hero_id:
                MatchDraft.objects.get_or_create(
                    match=match,
                    pick_order=pb.get('order', 0),
                    defaults={
                        'hero_id': hero_id if Hero.objects.filter(id=hero_id).exists() else None,
                        'team': pb.get('team', 0),
                        'is_pick': pb.get('is_pick', False),
                    }
                )

        # Save player performance data — all 10 players for match detail
        players_data = data.get('players', [])
        for p in players_data:
            p_account_id = p.get('account_id')
            if p_account_id is None:
                continue

            # Get or create a Player record (stub for non-tracked players)
            db_player, _ = Player.objects.get_or_create(
                account_id=p_account_id,
                defaults={
                    'personaname': p.get('personaname', '') or '',
                    'sync_status': Player.SyncStatus.PENDING,
                }
            )

            _save_player_match(match, db_player, p)


def _save_player_match(match, db_player, p):
    """Create PlayerMatch record from API data."""
    player_slot = p.get('player_slot', 0)
    is_radiant = player_slot < 128
    radiant_win = p.get('radiant_win')
    win = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)

    deaths = p.get('deaths', 0)
    kills = p.get('kills', 0)
    assists = p.get('assists', 0)
    kda = (kills + assists) / max(deaths, 1)

    hero_id = p.get('hero_id')

    PlayerMatch.objects.update_or_create(
        match=match,
        player=db_player,
        defaults={
            'hero_id': hero_id if hero_id and Hero.objects.filter(id=hero_id).exists() else None,
            'player_slot': player_slot,
            'is_radiant': is_radiant,
            'win': bool(win),
            'kills': kills,
            'deaths': deaths,
            'assists': assists,
            'kda': round(kda, 2),
            'last_hits': p.get('last_hits', 0),
            'denies': p.get('denies', 0),
            'gold_per_min': p.get('gold_per_min', 0),
            'xp_per_min': p.get('xp_per_min', 0),
            'level': p.get('level', 0),
            'hero_damage': p.get('hero_damage', 0),
            'hero_healing': p.get('hero_healing', 0),
            'tower_damage': p.get('tower_damage', 0),
            'lane': p.get('lane'),
            'lane_role': p.get('lane_role'),
            'lane_efficiency': p.get('lane_efficiency'),
            'camps_stacked': p.get('camps_stacked', 0),
            'obs_placed': p.get('obs_placed', 0),
            'sen_placed': p.get('sen_placed', 0),
            'actions_per_min': p.get('actions_per_min', 0),
            'stuns_seconds': p.get('stuns', 0.0),
            'neutral_kills': p.get('neutral_kills', 0),
            'items_final': {
                f'slot_{i}': p.get(f'item_{i}', 0) for i in range(6)
            },
            'purchase_log': p.get('purchase_log') or [],
            'gold_timeline': p.get('gold_t') or [],
            'xp_timeline': p.get('xp_t') or [],
            'lh_timeline': p.get('lh_t') or [],
            'ability_upgrades': p.get('ability_upgrades_arr') or [],
            'damage_targets': p.get('damage_targets') or {},
            'runes_log': p.get('runes_log') or [],
            'buyback_log': p.get('buyback_log') or [],
            'party_size': p.get('party_size'),
            'rank_tier': p.get('rank_tier'),
        }
    )


def _ensure_player_match(player, match_id, summary):
    """Ensure a PlayerMatch exists even if we already have the Match.
    Also fixes hero_id if it was NULL (heroes weren't loaded during initial sync)."""
    hero_id = summary.get('hero_id')
    valid_hero_id = hero_id if hero_id and Hero.objects.filter(id=hero_id).exists() else None

    existing = PlayerMatch.objects.filter(match_id=match_id, player=player).first()
    if existing:
        # Update hero_id if it was missing
        if existing.hero_id is None and valid_hero_id:
            existing.hero_id = valid_hero_id
            existing.save(update_fields=['hero_id'])
        return

    try:
        match = Match.objects.get(match_id=match_id)
    except Match.DoesNotExist:
        return

    player_slot = summary.get('player_slot', 0)
    is_radiant = player_slot < 128
    radiant_win = summary.get('radiant_win')
    win = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
    kills = summary.get('kills', 0)
    deaths = summary.get('deaths', 0)
    assists = summary.get('assists', 0)
    hero_id = summary.get('hero_id')

    PlayerMatch.objects.create(
        match=match,
        player=player,
        hero_id=hero_id if hero_id and Hero.objects.filter(id=hero_id).exists() else None,
        player_slot=player_slot,
        is_radiant=is_radiant,
        win=bool(win),
        kills=kills,
        deaths=deaths,
        assists=assists,
        kda=round((kills + assists) / max(deaths, 1), 2),
        gold_per_min=summary.get('gold_per_min', 0) if 'gold_per_min' in summary else 0,
        xp_per_min=summary.get('xp_per_min', 0) if 'xp_per_min' in summary else 0,
    )


def _update_hero_stats(client, player):
    """Aggregate player's match data into per-hero stats."""
    from django.db.models import Avg, Count, Sum, Max, Case, When, Value, IntegerField

    # 1. Fetch Global Lifetime Stats from OpenDota (gives true games/wins counts)
    import time
    global_map = {}
    for attempt in range(2):
        try:
            if attempt > 0:
                time.sleep(3)  # Wait before retry to avoid rate limit
            global_heroes = client.get_player_heroes(player.account_id)
            if global_heroes:
                global_map = {str(h['hero_id']): h for h in global_heroes}
                break
            else:
                logger.warning(f'Empty response from /heroes for {player.account_id}, attempt {attempt+1}')
        except Exception as e:
            logger.warning(f'Attempt {attempt+1} failed to fetch global heroes for {player.account_id}: {e}')
    
    if not global_map:
        logger.error(f'Could not fetch global heroes for {player.account_id} after retries, skipping hero stats update')
        return

    # 2. Aggregate Recent Detailed Stats from local DB (for GPM, KDA, etc)
    recent_data = (
        PlayerMatch.objects
        .filter(player=player)
        .values('hero_id')
        .annotate(
            local_games=Count('id'),
            avg_kda=Avg('kda'),
            avg_gpm=Avg('gold_per_min'),
            avg_xpm=Avg('xp_per_min'),
            avg_hero_damage=Avg('hero_damage'),
            avg_tower_damage=Avg('tower_damage'),
            avg_last_hits=Avg('last_hits'),
            last_played=Max('match__start_time'),
        )
    )

    recent_map = {hd['hero_id']: hd for hd in recent_data if hd['hero_id']}

    # 3. Merge and Save
    # We want to keep records for all heroes the player has played (at least globally)
    # But to prevent creating 120 blank rows, let's only create rows where they played > 0 games.
    
    all_played_heroes = set(int(h) for h in global_map.keys()) | set(recent_map.keys())
    
    for hero_id in all_played_heroes:
        g_stats = global_map.get(str(hero_id), {})
        r_stats = recent_map.get(hero_id, {})
        
        games_played = g_stats.get('games', 0)
        wins = g_stats.get('win', 0)
        
        # Fallback to local count if global fails for some reason
        if not games_played and r_stats:
            games_played = r_stats.get('local_games', 0)
            
        if games_played == 0:
            continue

        PlayerHeroStats.objects.update_or_create(
            player=player,
            hero_id=hero_id,
            defaults={
                'games_played': games_played,
                'wins': wins,
                'avg_kda': round(r_stats.get('avg_kda') or 0, 2),
                'avg_gpm': round(r_stats.get('avg_gpm') or 0, 2),
                'avg_xpm': round(r_stats.get('avg_xpm') or 0, 2),
                'avg_hero_damage': round(r_stats.get('avg_hero_damage') or 0, 2),
                'avg_tower_damage': round(r_stats.get('avg_tower_damage') or 0, 2),
                'avg_last_hits': round(r_stats.get('avg_last_hits') or 0, 2),
                'last_played': r_stats.get('last_played') if r_stats else None,
            }
        )

    logger.info(f'Hero stats updated for {player.personaname} (Global + Recent merged)')

    logger.info(f'Updated hero stats for {player.personaname}')

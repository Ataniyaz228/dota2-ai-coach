from collections import defaultdict
from datetime import datetime, timezone

from django.db.models import Avg, Count, Sum, Q, F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from players.models import Player
from players.serializers import PlayerSerializer
from matches.models import (
    Hero, Match, PlayerMatch, PlayerHeroStats, HeroBenchmark,
)
from matches.serializers import (
    HeroSerializer, PlayerMatchSerializer, MatchDetailSerializer,
    PlayerHeroStatsSerializer,
)


@api_view(['GET'])
def dashboard_overview(request, account_id):
    """Main dashboard: player info + recent stats summary."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

    # Recent matches stats
    recent = (
        PlayerMatch.objects
        .filter(player=player)
        .order_by('-match__start_time')[:20]
    )

    recent_list = list(recent)
    total = len(recent_list)
    wins = sum(1 for m in recent_list if m.win)
    winrate = wins / total if total > 0 else 0

    avg_kda = sum(m.kda for m in recent_list) / total if total > 0 else 0
    avg_gpm = sum(m.gold_per_min for m in recent_list) / total if total > 0 else 0

    # Top heroes (most played recently)
    top_heroes = (
        PlayerHeroStats.objects
        .filter(player=player)
        .select_related('hero')
        .order_by('-games_played')[:5]
    )

    return Response({
        'player': PlayerSerializer(player).data,
        'sync_status': player.sync_status,
        'last_synced_at': player.last_synced_at,
        'stats': {
            'total_matches': PlayerMatch.objects.filter(player=player).count(),
            'recent_matches_analyzed': total,
            'recent_winrate': round(winrate, 3),
            'recent_avg_kda': round(avg_kda, 2),
            'recent_avg_gpm': round(avg_gpm, 0),
            'lifetime_matches': player.lifetime_matches,
            'lifetime_wins': player.lifetime_wins,
        },
        'top_heroes': PlayerHeroStatsSerializer(top_heroes, many=True).data,
    })


@api_view(['GET'])
def dashboard_matches(request, account_id):
    """Paginated match list for a player."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

    hero_id = request.query_params.get('hero_id')
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))

    qs = (
        PlayerMatch.objects
        .filter(player=player)
        .select_related('match', 'hero')
        .order_by('-match__start_time')
    )

    if hero_id:
        qs = qs.filter(hero_id=hero_id)

    total = qs.count()
    matches = qs[offset:offset + limit]

    return Response({
        'total': total,
        'offset': offset,
        'limit': limit,
        'results': PlayerMatchSerializer(matches, many=True).data,
    })


@api_view(['GET'])
def dashboard_match_detail(request, match_id):
    """Full match detail with all player performances and draft."""
    try:
        match = (
            Match.objects
            .prefetch_related(
                'draft__hero',
                'player_performances__hero',
                'player_performances__player',
            )
            .get(match_id=match_id)
        )
    except Match.DoesNotExist:
        return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(MatchDetailSerializer(match).data)


@api_view(['GET'])
def dashboard_heroes(request, account_id):
    """All hero stats for a player."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

    hero_stats = (
        PlayerHeroStats.objects
        .filter(player=player)
        .select_related('hero')
        .order_by('-games_played')
    )

    return Response(PlayerHeroStatsSerializer(hero_stats, many=True).data)


@api_view(['GET'])
def dashboard_trends(request, account_id):
    """Time-series data for charts (GPM, KDA, etc. over time)."""
    try:
        player = Player.objects.get(account_id=account_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

    metric = request.query_params.get('metric', 'gold_per_min')
    limit = int(request.query_params.get('limit', 30))

    valid_metrics = ['gold_per_min', 'xp_per_min', 'kda', 'last_hits', 'hero_damage', 'deaths']
    if metric not in valid_metrics:
        return Response(
            {'error': f'Invalid metric. Valid: {valid_metrics}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    matches = (
        PlayerMatch.objects
        .filter(player=player)
        .select_related('match')
        .order_by('-match__start_time')[:limit]
    )

    data_points = []
    values = []

    for pm in reversed(list(matches)):
        value = getattr(pm, metric, 0)
        values.append(value)
        data_points.append({
            'date': pm.match.start_time.strftime('%Y-%m-%d'),
            'match_id': pm.match.match_id,
            'value': value,
            'hero': pm.hero.localized_name if pm.hero else 'Unknown',
            'win': pm.win,
        })

    avg_value = sum(values) / len(values) if values else 0

    return Response({
        'metric': metric,
        'data_points': data_points,
        'avg': round(avg_value, 1),
        'total_matches': len(data_points),
    })


@api_view(['GET'])
def heroes_list(request):
    """List all heroes (reference data)."""
    heroes = Hero.objects.all().order_by('localized_name')
    return Response(HeroSerializer(heroes, many=True).data)

from django.db import models


class Hero(models.Model):
    """Dota 2 hero reference data from OpenDota."""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)  # e.g. npc_dota_hero_antimage
    localized_name = models.CharField(max_length=100)  # e.g. Anti-Mage
    primary_attr = models.CharField(max_length=10, blank=True, default='')
    attack_type = models.CharField(max_length=20, blank=True, default='')
    roles = models.JSONField(default=list, blank=True)
    img_url = models.CharField(max_length=300, blank=True, default='')

    class Meta:
        db_table = 'heroes'

    def __str__(self):
        return self.localized_name


class Match(models.Model):
    """Core match data — shared across all players in the match."""
    match_id = models.BigIntegerField(primary_key=True)
    duration_seconds = models.IntegerField()
    game_mode = models.IntegerField(default=0)
    lobby_type = models.IntegerField(default=0)
    cluster = models.IntegerField(null=True, blank=True)
    radiant_score = models.IntegerField(default=0)
    dire_score = models.IntegerField(default=0)
    radiant_win = models.BooleanField(null=True)
    first_blood_time = models.IntegerField(null=True, blank=True)
    patch = models.IntegerField(null=True, blank=True)
    radiant_gold_adv = models.JSONField(null=True, blank=True)
    radiant_xp_adv = models.JSONField(null=True, blank=True)
    start_time = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'matches'
        ordering = ['-start_time']

    def __str__(self):
        return f'Match {self.match_id}'

    @property
    def duration_display(self):
        m, s = divmod(self.duration_seconds, 60)
        return f'{m}:{s:02d}'


class PlayerMatch(models.Model):
    """Per-player performance data in a specific match.
    This is the central analytics table."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_performances')
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='match_performances')
    hero = models.ForeignKey(Hero, on_delete=models.SET_NULL, null=True, related_name='match_performances')

    player_slot = models.IntegerField()
    is_radiant = models.BooleanField()
    win = models.BooleanField()

    # Core performance
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    kda = models.FloatField(default=0.0)

    # Economy
    last_hits = models.IntegerField(default=0)
    denies = models.IntegerField(default=0)
    gold_per_min = models.IntegerField(default=0)
    xp_per_min = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

    # Impact
    hero_damage = models.IntegerField(default=0)
    hero_healing = models.IntegerField(default=0)
    tower_damage = models.IntegerField(default=0)

    # Laning
    lane = models.IntegerField(null=True, blank=True)
    lane_role = models.IntegerField(null=True, blank=True)
    lane_efficiency = models.FloatField(null=True, blank=True)

    # Team utility
    camps_stacked = models.IntegerField(default=0)
    obs_placed = models.IntegerField(default=0)
    sen_placed = models.IntegerField(default=0)
    actions_per_min = models.IntegerField(default=0)
    stuns_seconds = models.FloatField(default=0.0)
    neutral_kills = models.IntegerField(default=0)

    # JSON fields for detailed timelines
    items_final = models.JSONField(default=dict, blank=True)  # {slot_0: item_id, ...}
    purchase_log = models.JSONField(default=list, blank=True)  # [{time, key}, ...]
    gold_timeline = models.JSONField(default=list, blank=True)  # [gold_at_min_0, ...]
    xp_timeline = models.JSONField(default=list, blank=True)
    lh_timeline = models.JSONField(default=list, blank=True)
    ability_upgrades = models.JSONField(default=list, blank=True)
    damage_targets = models.JSONField(default=dict, blank=True)
    runes_log = models.JSONField(default=list, blank=True)
    buyback_log = models.JSONField(default=list, blank=True)

    party_size = models.IntegerField(null=True, blank=True)
    rank_tier = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'player_matches'
        unique_together = ('match', 'player')
        indexes = [
            models.Index(fields=['player', 'hero', 'lane_role']),
        ]

    def __str__(self):
        hero_name = self.hero.localized_name if self.hero else 'Unknown'
        return f'{self.player} as {hero_name} in {self.match_id}'


class MatchDraft(models.Model):
    """Draft picks and bans for a match."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='draft')
    hero = models.ForeignKey(Hero, on_delete=models.SET_NULL, null=True)
    team = models.IntegerField()  # 0 = Radiant, 1 = Dire
    pick_order = models.IntegerField()
    is_pick = models.BooleanField()

    class Meta:
        db_table = 'match_draft'

    def __str__(self):
        action = 'Pick' if self.is_pick else 'Ban'
        return f'{action}: {self.hero} (order {self.pick_order})'


class HeroBenchmark(models.Model):
    """Percentile benchmark data for hero performance metrics."""
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name='benchmarks')
    metric = models.CharField(max_length=50)  # e.g. gold_per_min, xp_per_min
    percentiles = models.JSONField(default=list)  # [{percentile: 0.5, value: 500}, ...]
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hero_benchmarks'
        unique_together = ('hero', 'metric')

    def __str__(self):
        return f'{self.hero} — {self.metric}'

    def get_percentile_for_value(self, value):
        """Find which percentile a given value falls into."""
        if not self.percentiles:
            return None
        sorted_p = sorted(self.percentiles, key=lambda x: x.get('value', 0))
        for entry in reversed(sorted_p):
            if value >= entry.get('value', 0):
                return entry.get('percentile', 0)
        return 0.0


class PlayerHeroStats(models.Model):
    """Aggregated stats per hero per player — updated after sync."""
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='hero_stats')
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name='player_stats')
    games_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    avg_kda = models.FloatField(default=0.0)
    avg_gpm = models.FloatField(default=0.0)
    avg_xpm = models.FloatField(default=0.0)
    avg_hero_damage = models.FloatField(default=0.0)
    avg_tower_damage = models.FloatField(default=0.0)
    avg_last_hits = models.FloatField(default=0.0)
    last_played = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'player_hero_stats'
        unique_together = ('player', 'hero')

    def __str__(self):
        return f'{self.player} — {self.hero} ({self.games_played} games)'

    @property
    def winrate(self):
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

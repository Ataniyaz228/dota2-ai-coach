from django.db import models


class Player(models.Model):
    """Dota 2 player profile linked to Steam account."""

    class SyncStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SYNCING = 'syncing', 'Syncing'
        READY = 'ready', 'Ready'
        ERROR = 'error', 'Error'

    account_id = models.BigIntegerField(unique=True, db_index=True)
    steam_id_64 = models.BigIntegerField(null=True, blank=True)
    personaname = models.CharField(max_length=255, blank=True, default='')
    avatar_url = models.URLField(max_length=500, blank=True, default='')
    rank_tier = models.IntegerField(null=True, blank=True)
    leaderboard_rank = models.IntegerField(null=True, blank=True)
    estimated_mmr = models.IntegerField(null=True, blank=True)

    lifetime_wins = models.IntegerField(default=0)
    lifetime_matches = models.IntegerField(default=0)

    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING,
    )
    last_synced_match_id = models.BigIntegerField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'players'

    def __str__(self):
        return f'{self.personaname} ({self.account_id})'

    @property
    def rank_display(self):
        """Convert rank_tier integer to human-readable rank."""
        if not self.rank_tier:
            return 'Uncalibrated'
        rank_names = {
            1: 'Herald', 2: 'Guardian', 3: 'Crusader', 4: 'Archon',
            5: 'Legend', 6: 'Ancient', 7: 'Divine', 8: 'Immortal',
        }
        tier = self.rank_tier // 10
        stars = self.rank_tier % 10
        name = rank_names.get(tier, 'Unknown')
        if tier == 8:
            return 'Immortal'
        return f'{name} {stars}' if stars else name

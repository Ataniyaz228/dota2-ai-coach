from rest_framework import serializers
from players.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    rank_display = serializers.ReadOnlyField()

    class Meta:
        model = Player
        fields = [
            'id', 'account_id', 'steam_id_64', 'personaname', 'avatar_url',
            'rank_tier', 'rank_display', 'leaderboard_rank', 'estimated_mmr',
            'sync_status', 'last_synced_at', 'created_at',
            'lifetime_wins', 'lifetime_matches',
        ]
        read_only_fields = fields


class LinkAccountSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()

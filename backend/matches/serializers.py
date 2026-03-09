from rest_framework import serializers
from matches.models import (
    Hero, Match, PlayerMatch, MatchDraft,
    HeroBenchmark, PlayerHeroStats,
)


class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = ['id', 'name', 'localized_name', 'primary_attr', 'attack_type', 'roles', 'img_url']


class MatchListSerializer(serializers.ModelSerializer):
    """Lightweight match serializer for lists."""
    duration_display = serializers.ReadOnlyField()

    class Meta:
        model = Match
        fields = [
            'match_id', 'duration_seconds', 'duration_display',
            'game_mode', 'lobby_type', 'radiant_win',
            'radiant_score', 'dire_score', 'start_time',
        ]


class PlayerMatchSerializer(serializers.ModelSerializer):
    """Player performance in a match — for match lists."""
    hero = HeroSerializer(read_only=True)
    match = MatchListSerializer(read_only=True)

    class Meta:
        model = PlayerMatch
        fields = [
            'id', 'match', 'hero', 'player_slot', 'is_radiant', 'win',
            'kills', 'deaths', 'assists', 'kda',
            'gold_per_min', 'xp_per_min', 'last_hits', 'denies',
            'hero_damage', 'tower_damage', 'level', 'lane_role',
        ]


class PlayerMatchDetailSerializer(serializers.ModelSerializer):
    """Full player match data including timelines — for match detail view."""
    hero = HeroSerializer(read_only=True)

    class Meta:
        model = PlayerMatch
        fields = '__all__'


class MatchDraftSerializer(serializers.ModelSerializer):
    hero = HeroSerializer(read_only=True)

    class Meta:
        model = MatchDraft
        fields = ['hero', 'team', 'pick_order', 'is_pick']


class MatchDetailSerializer(serializers.ModelSerializer):
    """Full match data with draft and player performance."""
    duration_display = serializers.ReadOnlyField()
    draft = MatchDraftSerializer(many=True, read_only=True)
    player_performances = PlayerMatchDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id', 'duration_seconds', 'duration_display',
            'game_mode', 'lobby_type', 'cluster',
            'radiant_score', 'dire_score', 'radiant_win',
            'first_blood_time', 'patch',
            'radiant_gold_adv', 'radiant_xp_adv',
            'start_time', 'draft', 'player_performances',
        ]


class PlayerHeroStatsSerializer(serializers.ModelSerializer):
    hero = HeroSerializer(read_only=True)
    winrate = serializers.ReadOnlyField()

    class Meta:
        model = PlayerHeroStats
        fields = [
            'hero', 'games_played', 'wins', 'winrate',
            'avg_kda', 'avg_gpm', 'avg_xpm',
            'avg_hero_damage', 'avg_tower_damage', 'avg_last_hits',
            'last_played', 'updated_at',
        ]


class HeroBenchmarkSerializer(serializers.ModelSerializer):
    hero = HeroSerializer(read_only=True)

    class Meta:
        model = HeroBenchmark
        fields = ['hero', 'metric', 'percentiles', 'fetched_at']

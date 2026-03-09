export interface Player {
    id: number;
    account_id: number;
    steam_id_64: number | null;
    personaname: string;
    avatar_url: string;
    rank_tier: number | null;
    rank_display: string;
    leaderboard_rank: number | null;
    estimated_mmr: number | null;
    sync_status: 'pending' | 'syncing' | 'ready' | 'error';
    last_synced_at: string | null;
    created_at: string;
}

export interface Hero {
    id: number;
    name: string;
    localized_name: string;
    primary_attr: string;
    attack_type: string;
    roles: string[];
    img_url: string;
}

export interface MatchSummary {
    match_id: number;
    duration_seconds: number;
    duration_display: string;
    game_mode: number;
    lobby_type: number;
    radiant_win: boolean;
    radiant_score: number;
    dire_score: number;
    start_time: string;
}

export interface PlayerMatchEntry {
    id: number;
    match: MatchSummary;
    hero: Hero;
    player_slot: number;
    is_radiant: boolean;
    win: boolean;
    kills: number;
    deaths: number;
    assists: number;
    kda: number;
    gold_per_min: number;
    xp_per_min: number;
    last_hits: number;
    denies: number;
    hero_damage: number;
    tower_damage: number;
    level: number;
    lane_role: number | null;
}

export interface DashboardOverview {
    player: Player;
    sync_status: string;
    last_synced_at: string | null;
    stats: {
        total_matches: number;
        recent_matches_analyzed: number;
        recent_winrate: number;
        recent_avg_kda: number;
        recent_avg_gpm: number;
    };
    top_heroes: HeroStat[];
}

export interface HeroStat {
    hero: Hero;
    games_played: number;
    wins: number;
    winrate: number;
    avg_kda: number;
    avg_gpm: number;
    avg_xpm: number;
    avg_hero_damage: number;
    avg_tower_damage: number;
    avg_last_hits: number;
    last_played: string | null;
}

export interface TrendData {
    metric: string;
    data_points: TrendPoint[];
    avg: number;
    total_matches: number;
}

export interface TrendPoint {
    date: string;
    match_id: number;
    value: number;
    hero: string;
    win: boolean;
}

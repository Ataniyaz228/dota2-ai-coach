"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
    getDashboardOverview,
    getDashboardMatches,
    getDashboardTrends,
    triggerSync,
} from "@/lib/api";
import type {
    DashboardOverview,
    PlayerMatchEntry,
    TrendData,
} from "@/lib/types";
import TrendChart from "@/components/TrendChart";
import { parseRankTier, formatMmrRange } from "@/lib/ranks";

function DashboardContent() {
    const searchParams = useSearchParams();
    const accountId = parseInt(searchParams.get("id") || "0");

    const [overview, setOverview] = useState<DashboardOverview | null>(null);
    const [matches, setMatches] = useState<PlayerMatchEntry[]>([]);
    const [trends, setTrends] = useState<TrendData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [syncing, setSyncing] = useState(false);
    const [trendMetric, setTrendMetric] = useState("gold_per_min");

    useEffect(() => {
        if (!accountId) return;
        loadData();
    }, [accountId]);

    useEffect(() => {
        if (!accountId) return;
        getDashboardTrends(accountId, trendMetric, 30)
            .then(setTrends)
            .catch(() => { });
    }, [accountId, trendMetric]);

    async function loadData() {
        setLoading(true);
        setError("");
        try {
            const [overviewData, matchesData] = await Promise.all([
                getDashboardOverview(accountId),
                getDashboardMatches(accountId, { limit: "20" }),
            ]);
            setOverview(overviewData);
            setMatches(matchesData.results || []);

            if (
                overviewData.sync_status === "syncing" ||
                overviewData.sync_status === "pending"
            ) {
                setSyncing(true);
                setTimeout(loadData, 5000);
            } else {
                setSyncing(false);
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Ошибка загрузки данных");
        } finally {
            setLoading(false);
        }
    }

    async function handleSync() {
        setSyncing(true);
        try {
            await triggerSync(accountId);
            setTimeout(loadData, 3000);
        } catch {
            setSyncing(false);
        }
    }

    if (!accountId) {
        return (
            <div className="container">
                <div className="empty-state" style={{ marginTop: 80 }}>
                    <p>Укажите Account ID: /dashboard?id=YOUR_ID</p>
                    <a href="/" className="btn btn-primary" style={{ marginTop: 16 }}>
                        На главную
                    </a>
                </div>
            </div>
        );
    }

    if (loading && !overview) {
        return (
            <div className="loading" style={{ marginTop: 100 }}>
                <div className="loading-spinner" />
                Загрузка данных...
            </div>
        );
    }

    if (error) {
        return (
            <div className="container">
                <div className="empty-state" style={{ marginTop: 80 }}>
                    <p>{error}</p>
                    <a href="/" className="btn btn-primary" style={{ marginTop: 16 }}>
                        Попробовать другой ID
                    </a>
                </div>
            </div>
        );
    }

    if (!overview) return null;

    const stats = overview.stats;
    const rank = parseRankTier(overview.player.rank_tier);

    return (
        <div className="container dashboard">
            {/* Header — compact, with status dot */}
            <div className="dash-header">
                <div className="dash-header-left">
                    {overview.player.avatar_url && (
                        <img
                            src={overview.player.avatar_url}
                            alt=""
                            className="dash-avatar"
                        />
                    )}
                    <div className="dash-identity">
                        <div className="dash-name">
                            {overview.player.personaname || "Player"}
                        </div>
                        <div className="dash-rank">
                            <span className="mono">{rank.display}</span>
                            {rank.mmrEstimate > 0 && (
                                <span className="dash-mmr">{formatMmrRange(rank)} MMR</span>
                            )}
                        </div>
                    </div>
                </div>
                <div className="dash-header-right">
                    <div className="dash-status">
                        <span className={`dash-status-dot ${syncing ? "syncing" : overview.sync_status === "ready" ? "ready" : ""}`} />
                        <span className="dash-status-text">
                            {syncing ? "Синхронизация" : "Данные актуальны"}
                        </span>
                    </div>
                    <button
                        className="dash-refresh"
                        onClick={handleSync}
                        disabled={syncing}
                        title="Обновить данные"
                        id="sync-btn"
                    >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 2v6h-6" /><path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
                            <path d="M3 22v-6h6" /><path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
                        </svg>
                    </button>
                </div>
            </div>

            {/* Metric cards — left-aligned, accent borders */}
            <div className="metric-grid">
                <MetricCard
                    value={stats.total_matches.toString()}
                    label="МАТЧЕЙ"
                    accent="var(--text-dim)"
                />
                <MetricCard
                    value={`${(stats.recent_winrate * 100).toFixed(1)}%`}
                    label="ВИНРЕЙТ (20)"
                    accent={stats.recent_winrate >= 0.5 ? "var(--win)" : "var(--loss)"}
                    valueColor={stats.recent_winrate >= 0.5 ? "var(--win)" : "var(--loss)"}
                />
                <MetricCard
                    value={stats.recent_avg_kda.toFixed(2)}
                    label="AVG KDA"
                    accent="var(--accent)"
                />
                <MetricCard
                    value={Math.round(stats.recent_avg_gpm).toString()}
                    label="AVG GPM"
                    accent="var(--accent)"
                />
            </div>

            <div className="dashboard-grid dashboard-grid-2" style={{ marginBottom: 24 }}>
                {/* Trend Chart */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Тренды</span>
                        <select
                            className="input"
                            style={{ width: 140 }}
                            value={trendMetric}
                            onChange={(e) => setTrendMetric(e.target.value)}
                            id="trend-metric-select"
                        >
                            <option value="gold_per_min">GPM</option>
                            <option value="xp_per_min">XPM</option>
                            <option value="kda">KDA</option>
                            <option value="last_hits">Last Hits</option>
                            <option value="hero_damage">Hero Damage</option>
                            <option value="deaths">Deaths</option>
                        </select>
                    </div>
                    <div className="chart-container">
                        {trends && trends.data_points.length > 0 ? (
                            <TrendChart data={trends} />
                        ) : (
                            <div className="empty-state">Нет данных</div>
                        )}
                    </div>
                </div>

                {/* Top Heroes */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Топ герои</span>
                    </div>
                    {overview.top_heroes.length > 0 ? (
                        <div style={{ display: "flex", flexDirection: "column" }}>
                            {overview.top_heroes.map((hs, i) => (
                                <div
                                    key={hs.hero.id}
                                    className="hero-card"
                                    style={{
                                        borderBottom: i < overview.top_heroes.length - 1
                                            ? "1px solid var(--border-primary)"
                                            : "none",
                                    }}
                                >
                                    {hs.hero.img_url && (
                                        <img src={hs.hero.img_url} alt={hs.hero.localized_name} />
                                    )}
                                    <div className="hero-card-info">
                                        <div className="hero-card-name">{hs.hero.localized_name}</div>
                                        <div className="hero-card-stats">
                                            <span>{hs.games_played} игр</span>
                                            <span>KDA {hs.avg_kda.toFixed(1)}</span>
                                            <span>GPM {Math.round(hs.avg_gpm)}</span>
                                        </div>
                                    </div>
                                    <div
                                        className="hero-card-winrate"
                                        style={{
                                            color: hs.winrate >= 0.5 ? "var(--win)" : "var(--loss)",
                                        }}
                                    >
                                        {(hs.winrate * 100).toFixed(0)}%
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">Нет данных по героям</div>
                    )}
                </div>
            </div>

            {/* Match History */}
            <div className="card">
                <div className="card-header">
                    <span className="card-title">История матчей</span>
                </div>
                {matches.length > 0 ? (
                    <table className="match-table">
                        <thead>
                            <tr>
                                <th>Герой</th>
                                <th>Результат</th>
                                <th>KDA</th>
                                <th>GPM / XPM</th>
                                <th>LH / DN</th>
                                <th>Урон</th>
                                <th>Длительность</th>
                            </tr>
                        </thead>
                        <tbody>
                            {matches.map((pm) => (
                                <tr
                                    key={pm.id}
                                    className={`match-row ${pm.win ? "win" : "loss"}`}
                                    onClick={() => window.location.href = `/match/${pm.match.match_id}`}
                                >
                                    <td>
                                        <div className="hero-avatar">
                                            {pm.hero?.img_url && (
                                                <img src={pm.hero.img_url} alt={pm.hero.localized_name} />
                                            )}
                                            <span className="hero-name">
                                                {pm.hero?.localized_name || "—"}
                                            </span>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`badge ${pm.win ? "badge-win" : "badge-loss"}`}>
                                            {pm.win ? "W" : "L"}
                                        </span>
                                    </td>
                                    <td>
                                        <span className="kda">
                                            <span className="kda-kills">{pm.kills}</span>
                                            <span className="kda-sep">/</span>
                                            <span className="kda-deaths">{pm.deaths}</span>
                                            <span className="kda-sep">/</span>
                                            <span className="kda-assists">{pm.assists}</span>
                                        </span>
                                    </td>
                                    <td className="mono" style={{ fontSize: "0.78rem" }}>
                                        {pm.gold_per_min} / {pm.xp_per_min}
                                    </td>
                                    <td className="mono" style={{ fontSize: "0.78rem" }}>
                                        {pm.last_hits} / {pm.denies}
                                    </td>
                                    <td className="mono" style={{ fontSize: "0.78rem" }}>
                                        {(pm.hero_damage / 1000).toFixed(1)}k
                                    </td>
                                    <td className="mono" style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
                                        {pm.match.duration_display}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="empty-state">
                        {syncing ? "Данные загружаются..." : "Нет данных о матчах"}
                    </div>
                )}
            </div>
        </div>
    );
}

/* Metric card component */
function MetricCard({
    value,
    label,
    accent,
    valueColor,
}: {
    value: string;
    label: string;
    accent: string;
    valueColor?: string;
}) {
    return (
        <div className="metric-card" style={{ borderLeftColor: accent }}>
            <div
                className="metric-value"
                style={valueColor ? { color: valueColor } : undefined}
            >
                {value}
            </div>
            <div className="metric-label">{label}</div>
        </div>
    );
}

export default function DashboardPage() {
    return (
        <Suspense
            fallback={
                <div className="loading" style={{ marginTop: 100 }}>
                    <div className="loading-spinner" />
                    Загрузка...
                </div>
            }
        >
            <DashboardContent />
        </Suspense>
    );
}

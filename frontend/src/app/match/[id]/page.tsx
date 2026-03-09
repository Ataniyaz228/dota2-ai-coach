"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getMatchDetail } from "@/lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

export default function MatchDetailPage() {
    const params = useParams();
    const matchId = parseInt(params.id as string);

    const [match, setMatch] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!matchId) return;
        getMatchDetail(matchId)
            .then(setMatch)
            .catch((err: Error) => setError(err.message))
            .finally(() => setLoading(false));
    }, [matchId]);

    if (loading) {
        return (
            <div className="loading" style={{ marginTop: 100 }}>
                <div className="loading-spinner" />
                Загрузка матча...
            </div>
        );
    }

    if (error || !match) {
        return (
            <div className="container">
                <div className="empty-state" style={{ marginTop: 80 }}>
                    <p>{error || "Матч не найден"}</p>
                    <a href="/" className="btn btn-primary" style={{ marginTop: 16 }}>
                        На главную
                    </a>
                </div>
            </div>
        );
    }

    const radiantPlayers = (match.player_performances || []).filter(
        (p: any) => p.player_slot < 128
    );
    const direPlayers = (match.player_performances || []).filter(
        (p: any) => p.player_slot >= 128
    );
    const totalPlayers = radiantPlayers.length + direPlayers.length;
    const missingPlayers = 10 - totalPlayers;

    return (
        <div className="container dashboard">
            {/* Match Header */}
            <div style={{ marginBottom: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                    <h1 style={{ fontSize: "1.1rem", fontWeight: 600, letterSpacing: "-0.01em" }}>
                        <span className="mono" style={{ color: "var(--text-muted)" }}>#{match.match_id}</span>
                    </h1>
                    <span className={`badge ${match.radiant_win ? "badge-win" : "badge-loss"}`}>
                        {match.radiant_win ? "RADIANT" : "DIRE"}
                    </span>
                </div>

                <div className="stat-grid" style={{ gridTemplateColumns: "repeat(5, 1fr)" }}>
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: "1.3rem" }}>
                            {match.duration_display}
                        </div>
                        <div className="stat-label">Длительность</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: "1.3rem", color: "var(--win)" }}>
                            {match.radiant_score}
                        </div>
                        <div className="stat-label">Radiant</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: "1.3rem", color: "var(--loss)" }}>
                            {match.dire_score}
                        </div>
                        <div className="stat-label">Dire</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: "1.3rem" }}>
                            {match.first_blood_time
                                ? `${Math.floor(match.first_blood_time / 60)}:${(match.first_blood_time % 60).toString().padStart(2, "0")}`
                                : "—"}
                        </div>
                        <div className="stat-label">First Blood</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value" style={{ fontSize: "1.3rem" }}>
                            {match.game_mode}
                        </div>
                        <div className="stat-label">Режим</div>
                    </div>
                </div>
            </div>

            {/* Radiant */}
            <TeamTable title="RADIANT" players={radiantPlayers} isWinner={match.radiant_win} />

            {/* Dire */}
            <TeamTable title="DIRE" players={direPlayers} isWinner={!match.radiant_win} />

            {/* Anonymous notice */}
            {missingPlayers > 0 && (
                <div
                    style={{
                        marginTop: 12,
                        padding: "10px 16px",
                        background: "var(--bg-surface)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "var(--radius)",
                        color: "var(--text-dim)",
                        fontSize: "0.75rem",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                    }}
                >
                    <span style={{ color: "var(--caution)", fontFamily: "'JetBrains Mono', monospace" }}>
                        {missingPlayers}
                    </span>
                    <span>
                        {missingPlayers === 1
                            ? "игрок скрыт"
                            : missingPlayers < 5
                                ? "игрока скрыты"
                                : "игроков скрыты"}{" "}
                        — анонимные профили в OpenDota
                    </span>
                </div>
            )}

            {/* Back */}
            <div style={{ marginTop: 24 }}>
                <button className="btn btn-ghost" onClick={() => window.history.back()}>
                    ← Назад
                </button>
            </div>
        </div>
    );
}

function TeamTable({
    title,
    players,
    isWinner,
}: {
    title: string;
    players: any[];
    isWinner: boolean;
}) {
    return (
        <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-header">
                <span className="card-title">
                    {title}
                    {isWinner && (
                        <span className="badge badge-win" style={{ marginLeft: 6 }}>
                            W
                        </span>
                    )}
                </span>
            </div>
            <table className="match-table">
                <thead>
                    <tr>
                        <th>Герой</th>
                        <th>KDA</th>
                        <th>GPM</th>
                        <th>XPM</th>
                        <th>LH/DN</th>
                        <th>Урон героям</th>
                        <th>Урон строениям</th>
                        <th>Лечение</th>
                        <th>LVL</th>
                    </tr>
                </thead>
                <tbody>
                    {players.map((p: any, i: number) => (
                        <tr key={i} className="match-row">
                            <td>
                                <div className="hero-avatar">
                                    {p.hero?.img_url && (
                                        <img src={p.hero.img_url} alt={p.hero?.localized_name} />
                                    )}
                                    <span className="hero-name">
                                        {p.hero?.localized_name || "—"}
                                    </span>
                                </div>
                            </td>
                            <td>
                                <span className="kda">
                                    <span className="kda-kills">{p.kills}</span>
                                    <span className="kda-sep">/</span>
                                    <span className="kda-deaths">{p.deaths}</span>
                                    <span className="kda-sep">/</span>
                                    <span className="kda-assists">{p.assists}</span>
                                </span>
                            </td>
                            <td className="mono">{p.gold_per_min}</td>
                            <td className="mono">{p.xp_per_min}</td>
                            <td className="mono">{p.last_hits}/{p.denies}</td>
                            <td className="mono">
                                {p.hero_damage ? `${(p.hero_damage / 1000).toFixed(1)}k` : "—"}
                            </td>
                            <td className="mono">
                                {p.tower_damage ? `${(p.tower_damage / 1000).toFixed(1)}k` : "—"}
                            </td>
                            <td className="mono">
                                {p.hero_healing ? `${(p.hero_healing / 1000).toFixed(1)}k` : "—"}
                            </td>
                            <td className="mono">{p.level}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

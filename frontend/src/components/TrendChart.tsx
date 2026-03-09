"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
} from "recharts";
import type { TrendData } from "@/lib/types";

interface TrendChartProps {
    data: TrendData;
    accountId?: number;
}

const METRIC_LABELS: Record<string, string> = {
    gold_per_min: "GPM",
    xp_per_min: "XPM",
    kda: "KDA",
    last_hits: "Last Hits",
    hero_damage: "Hero Damage",
    deaths: "Deaths",
};

/* eslint-disable @typescript-eslint/no-explicit-any */
function CustomTooltip({ active, payload, metric }: any) {
    if (!active || !payload || !payload.length) return null;
    const entry = payload[0].payload;
    const value = payload[0].value as number;
    const metricLabel = METRIC_LABELS[metric] || metric;
    const displayValue =
        metric === "hero_damage"
            ? `${(value / 1000).toFixed(1)}k`
            : value.toFixed(1);

    return (
        <div
            style={{
                background: "#1a1a1e",
                border: "1px solid #2e2e33",
                borderRadius: 3,
                padding: "8px 12px",
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 11,
                pointerEvents: "none",
            }}
        >
            <div style={{ color: "#4a4a50", fontSize: 10, marginBottom: 2 }}>{entry.dateLabel}</div>
            <div style={{ color: "#e4e4e7", fontWeight: 600 }}>
                {metricLabel}: {displayValue}
            </div>
            <div style={{ color: "#636369", fontSize: 10, marginTop: 2 }}>
                {entry.hero} · <span style={{ color: entry.win ? "#3ecf8e" : "#e5484d" }}>{entry.win ? "W" : "L"}</span>
            </div>
            <div style={{ color: "#38383f", fontSize: 9, marginTop: 4, borderTop: "1px solid #2e2e33", paddingTop: 3 }}>
                click → детали матча
            </div>
        </div>
    );
}
/* eslint-enable @typescript-eslint/no-explicit-any */

export default function TrendChart({ data, accountId }: TrendChartProps) {
    const router = useRouter();

    // Each data point gets a unique sequential index as X-axis key.
    // dateLabel is kept for tooltip and tick display only.
    const chartData = data.data_points.map((point, idx) => {
        const dateLabel = new Date(point.date).toLocaleDateString("ru-RU", {
            day: "numeric",
            month: "short",
        });
        return {
            ...point,
            idx,
            dateLabel,
        };
    });

    // Custom tick: show date label only on first occurrence of each date
    const shownDates = new Set<string>();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const renderTick = (props: any) => {
        const { x, y, payload } = props;
        const dp = chartData[payload.value];
        if (!dp) return <g />;
        const label = dp.dateLabel;
        if (shownDates.has(label)) return <g />;
        shownDates.add(label);
        return (
            <g transform={`translate(${x},${y})`}>
                <text
                    x={0}
                    y={0}
                    dy={12}
                    textAnchor="middle"
                    fill="#4a4a50"
                    fontSize={10}
                    fontFamily="'JetBrains Mono', monospace"
                >
                    {label}
                </text>
            </g>
        );
    };

    // Clickable activeDot component
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const ClickableDot = useCallback((props: any) => {
        const { cx, cy, payload } = props;
        if (cx == null || cy == null) return null;
        const matchId = payload?.match_id;

        return (
            <circle
                cx={cx}
                cy={cy}
                r={5}
                fill="#1a1a1e"
                stroke="#2dd4a8"
                strokeWidth={2}
                style={{ cursor: matchId ? "pointer" : "default" }}
                onClick={(e) => {
                    e.stopPropagation();
                    if (matchId) {
                        router.push(`/match/${matchId}${accountId ? `?account_id=${accountId}` : ''}`);
                    }
                }}
            />
        );
    }, [router]);

    return (
        <ResponsiveContainer width="100%" height="100%">
            <AreaChart
                data={chartData}
                margin={{ top: 8, right: 12, left: -4, bottom: 4 }}
            >
                <defs>
                    <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#2dd4a8" stopOpacity={0.15} />
                        <stop offset="90%" stopColor="#2dd4a8" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid
                    strokeDasharray="3 6"
                    stroke="rgba(46, 46, 51, 0.4)"
                    vertical={false}
                />
                <XAxis
                    dataKey="idx"
                    type="number"
                    domain={[0, chartData.length - 1]}
                    tick={renderTick}
                    axisLine={{ stroke: "#2e2e33" }}
                    tickLine={false}
                    tickCount={chartData.length}
                />
                <YAxis
                    tick={{ fill: "#4a4a50", fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                    axisLine={false}
                    tickLine={false}
                    width={40}
                />
                <Tooltip
                    content={<CustomTooltip metric={data.metric} />}
                    cursor={{ stroke: "#38383f", strokeWidth: 1 }}
                />
                <ReferenceLine
                    y={data.avg}
                    stroke="#38383f"
                    strokeDasharray="4 4"
                    label={{
                        value: `avg ${data.metric === "hero_damage" ? `${(data.avg / 1000).toFixed(1)}k` : data.avg.toFixed(1)}`,
                        position: "right",
                        fill: "#4a4a50",
                        fontSize: 9,
                        fontFamily: "'JetBrains Mono', monospace",
                    }}
                />
                <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#2dd4a8"
                    strokeWidth={1.5}
                    fill="url(#areaFill)"
                    dot={false}
                    activeDot={<ClickableDot />}
                />
            </AreaChart>
        </ResponsiveContainer>
    );
}

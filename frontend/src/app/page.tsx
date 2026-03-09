"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { linkAccount } from "@/lib/api";

export default function Home() {
  const [accountId, setAccountId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const parsed = parseInt(accountId.trim());
    if (isNaN(parsed) || parsed <= 0) {
      setError("Введите корректный Account ID (числовой)");
      return;
    }

    setLoading(true);
    try {
      await linkAccount(parsed);
      router.push(`/dashboard?id=${parsed}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Ошибка подключения");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="hero-section">
      {/* Tactical grid background */}
      <div className="hero-grid-bg" />
      <div className="hero-grid-fade" />

      <div className="hero-layout">
        {/* LEFT — Text + Terminal Input */}
        <div className="hero-left">
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            ANALYTICAL PLATFORM
          </div>

          <h1 className="hero-title">
            Dota 2 аналитика<br />
            <span className="hero-title-accent">на другом уровне</span>
          </h1>

          <p className="hero-desc">
            Детальный разбор матчей, выявление системных паттернов
            и персональные рекомендации для прогресса. Каждый матч —
            это данные. Мы превращаем их в actionable insights.
          </p>

          {/* Terminal-style input */}
          <div className="terminal-block">
            <div className="terminal-header">
              <span className="terminal-dot terminal-dot--r" />
              <span className="terminal-dot terminal-dot--y" />
              <span className="terminal-dot terminal-dot--g" />
              <span className="terminal-label">dotacoach query</span>
            </div>
            <form className="terminal-body" onSubmit={handleSubmit}>
              <div className="terminal-line">
                <span className="terminal-prompt">$</span>
                <input
                  type="text"
                  className="terminal-input"
                  placeholder="enter account_id"
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  id="account-id-input"
                  spellCheck={false}
                  autoComplete="off"
                />
                <button
                  type="submit"
                  className="terminal-run"
                  disabled={loading}
                  id="analyze-btn"
                >
                  {loading ? "..." : "RUN"}
                </button>
              </div>
              {error && (
                <div className="terminal-line terminal-error">
                  <span className="terminal-prompt" style={{ color: "var(--loss)" }}>!</span>
                  {error}
                </div>
              )}
            </form>
            <div className="terminal-hint">
              ID можно найти на{" "}
              <a href="https://www.opendota.com" target="_blank" rel="noreferrer">
                opendota.com
              </a>
            </div>
          </div>

          {/* Feature tags */}
          <div className="hero-tags">
            <span className="hero-tag">GPM / XPM тренды</span>
            <span className="hero-tag">AI-коучинг</span>
            <span className="hero-tag">Детализация матчей</span>
            <span className="hero-tag">Hero meta</span>
          </div>
        </div>

        {/* RIGHT — Dashboard Preview */}
        <div className="hero-right">
          <div className="preview-stack">
            {/* Floating stat cards */}
            <div className="preview-card preview-card--stats">
              <div className="preview-card-header">PERFORMANCE</div>
              <div className="preview-stats-grid">
                <div className="preview-stat">
                  <div className="preview-stat-value">487</div>
                  <div className="preview-stat-label">AVG GPM</div>
                </div>
                <div className="preview-stat">
                  <div className="preview-stat-value">12.4</div>
                  <div className="preview-stat-label">AVG KDA</div>
                </div>
                <div className="preview-stat">
                  <div className="preview-stat-value" style={{ color: "var(--win)" }}>62%</div>
                  <div className="preview-stat-label">WINRATE</div>
                </div>
                <div className="preview-stat">
                  <div className="preview-stat-value">693</div>
                  <div className="preview-stat-label">AVG XPM</div>
                </div>
              </div>
            </div>

            {/* Mini chart card */}
            <div className="preview-card preview-card--chart">
              <div className="preview-card-header">GPM TREND — 30 MATCHES</div>
              <div className="preview-chart">
                <svg viewBox="0 0 200 60" className="preview-svg">
                  <polyline
                    fill="none"
                    stroke="var(--accent)"
                    strokeWidth="1.5"
                    points="0,45 15,38 30,42 45,30 60,35 75,25 90,28 105,18 120,22 135,15 150,20 165,12 180,8 200,14"
                  />
                  <line x1="0" y1="30" x2="200" y2="30" stroke="#38383f" strokeWidth="0.5" strokeDasharray="3 3" />
                </svg>
              </div>
            </div>

            {/* Match history mini */}
            <div className="preview-card preview-card--matches">
              <div className="preview-card-header">RECENT MATCHES</div>
              <div className="preview-matches">
                {[
                  { hero: "Anti-Mage", kda: "8/2/5", w: true },
                  { hero: "Shadow Fiend", kda: "12/4/9", w: true },
                  { hero: "Invoker", kda: "3/7/6", w: false },
                  { hero: "Slark", kda: "15/3/8", w: true },
                ].map((m, i) => (
                  <div key={i} className="preview-match-row">
                    <span className={`preview-match-indicator ${m.w ? "w" : "l"}`} />
                    <span className="preview-match-hero">{m.hero}</span>
                    <span className="preview-match-kda">{m.kda}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom features strip */}
      <div className="hero-features-strip">
        <div className="hero-feature-item">
          <span className="hero-feature-num">01</span>
          <div>
            <div className="hero-feature-title">Аналитика матчей</div>
            <div className="hero-feature-desc">Детальные метрики каждого матча</div>
          </div>
        </div>
        <div className="hero-feature-item">
          <span className="hero-feature-num">02</span>
          <div>
            <div className="hero-feature-title">AI-рекомендации</div>
            <div className="hero-feature-desc">Паттерны ошибок и советы</div>
          </div>
        </div>
        <div className="hero-feature-item">
          <span className="hero-feature-num">03</span>
          <div>
            <div className="hero-feature-title">Тренды прогресса</div>
            <div className="hero-feature-desc">Визуализация роста по метрикам</div>
          </div>
        </div>
      </div>
    </main>
  );
}

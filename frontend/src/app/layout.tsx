import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aegis.ai — Аналитическая платформа для Dota 2",
  description: "Аналитический инструмент для игроков в Dota 2. Детальная статистика матчей, тренды производительности, персональный AI-коучинг.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>
        <nav className="navbar">
          <div className="navbar-inner">
            <a href="/" className="navbar-brand">
              <span className="logo-icon">AE</span>
              <span>Aegis.ai</span>
            </a>
            <div className="navbar-links">
              <a href="/">Главная</a>
              <a href="/dashboard">Аналитика</a>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}

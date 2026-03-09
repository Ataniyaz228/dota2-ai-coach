"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getCoachAnalysis, coachChat } from "@/lib/api";

interface CoachAnalysisProps {
    accountId: number;
}

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

export default function CoachAnalysis({ accountId }: CoachAnalysisProps) {
    const [analysis, setAnalysis] = useState<string | null>(null);
    const [dataSummary, setDataSummary] = useState<Record<string, string | number> | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // Chat state
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
    const [chatInput, setChatInput] = useState("");
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatMessages]);

    async function handleAnalyze() {
        setLoading(true);
        setError("");
        setAnalysis(null);
        setChatMessages([]);
        try {
            const result = await getCoachAnalysis(accountId);
            setAnalysis(result.analysis);
            setDataSummary(result.data_summary);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Ошибка анализа");
        } finally {
            setLoading(false);
        }
    }

    async function handleChat(e: React.FormEvent) {
        e.preventDefault();
        const text = chatInput.trim();
        if (!text || chatLoading) return;

        const userMsg: ChatMessage = { role: "user", content: text };
        const newMessages = [...chatMessages, userMsg];
        setChatMessages(newMessages);
        setChatInput("");
        setChatLoading(true);

        try {
            const result = await coachChat(accountId, newMessages);
            setChatMessages([...newMessages, { role: "assistant", content: result.reply }]);
        } catch {
            setChatMessages([
                ...newMessages,
                { role: "assistant", content: "Ошибка при обращении к AI. Попробуйте ещё раз." },
            ]);
        } finally {
            setChatLoading(false);
        }
    }

    return (
        <div className="card coach-card">
            <div className="card-header">
                <span className="card-title">
                    <span className="coach-icon">AI</span>
                    Персональный анализ
                </span>
                <button
                    className="btn btn-primary"
                    onClick={handleAnalyze}
                    disabled={loading}
                    id="coach-analyze-btn"
                    style={{ padding: "5px 14px", fontSize: "0.75rem" }}
                >
                    {loading ? "Анализирую..." : "Запустить анализ"}
                </button>
            </div>

            {/* Summary chips */}
            {dataSummary && (
                <div className="coach-summary">
                    <div className="coach-chip">
                        <span className="coach-chip-value mono">{dataSummary.matches_analyzed}</span>
                        <span className="coach-chip-label">матчей</span>
                    </div>
                    <div className="coach-chip">
                        <span className="coach-chip-value mono">{dataSummary.winrate}</span>
                        <span className="coach-chip-label">винрейт</span>
                    </div>
                    <div className="coach-chip">
                        <span className="coach-chip-value mono">{dataSummary.avg_kda}</span>
                        <span className="coach-chip-label">KDA</span>
                    </div>
                    <div className="coach-chip">
                        <span className="coach-chip-value mono">{dataSummary.avg_gpm}</span>
                        <span className="coach-chip-label">GPM</span>
                    </div>
                </div>
            )}

            {/* Loading state */}
            {loading && (
                <div className="coach-loading">
                    <div className="loading-spinner" />
                    <div>
                        <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                            AI анализирует ваши данные...
                        </div>
                        <div style={{ color: "var(--text-dim)", fontSize: "0.72rem", marginTop: 4 }}>
                            Обработка метрик, паттернов и героев
                        </div>
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div style={{ padding: 16, color: "var(--loss)", fontSize: "0.8rem" }}>
                    {error}
                </div>
            )}

            {/* Analysis result */}
            {analysis && !loading && (
                <div className="coach-result">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {analysis}
                    </ReactMarkdown>
                </div>
            )}

            {/* Chat messages */}
            {chatMessages.length > 0 && (
                <div className="coach-chat-history">
                    {chatMessages.map((msg, i) => (
                        <div key={i} className={`coach-msg coach-msg-${msg.role}`}>
                            <div className="coach-msg-label">
                                {msg.role === "user" ? "Вы" : "AI Coach"}
                            </div>
                            <div className="coach-msg-content">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {msg.content}
                                </ReactMarkdown>
                            </div>
                        </div>
                    ))}
                    {chatLoading && (
                        <div className="coach-msg coach-msg-assistant">
                            <div className="coach-msg-label">AI Coach</div>
                            <div className="coach-msg-content">
                                <div className="coach-typing">
                                    <span /><span /><span />
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>
            )}

            {/* Chat input — visible after analysis */}
            {analysis && !loading && (
                <form className="coach-chat-form" onSubmit={handleChat}>
                    <input
                        className="input coach-chat-input"
                        type="text"
                        placeholder="Задайте вопрос AI-тренеру..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        disabled={chatLoading}
                        id="coach-chat-input"
                    />
                    <button
                        type="submit"
                        className="btn btn-primary coach-chat-send"
                        disabled={chatLoading || !chatInput.trim()}
                    >
                        →
                    </button>
                </form>
            )}

            {/* Empty state */}
            {!analysis && !loading && !error && (
                <div className="coach-empty">
                    <div className="coach-empty-icon">◇</div>
                    <div>Нажмите «Запустить анализ» для получения<br />персонального разбора от AI-тренера</div>
                </div>
            )}
        </div>
    );
}

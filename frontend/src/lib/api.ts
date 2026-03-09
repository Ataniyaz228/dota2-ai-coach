const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchAPI(endpoint: string, options?: RequestInit) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || `API Error: ${res.status}`);
    }
    return res.json();
}

// Player
export const linkAccount = (accountId: number) =>
    fetchAPI('/profile/link', {
        method: 'POST',
        body: JSON.stringify({ account_id: accountId }),
    });

export const getPlayer = (accountId: number) =>
    fetchAPI(`/profile/${accountId}/`);

export const triggerSync = (accountId: number) =>
    fetchAPI(`/profile/${accountId}/sync`, { method: 'POST' });

// Dashboard
export const getDashboardOverview = (accountId: number) =>
    fetchAPI(`/dashboard/overview/${accountId}/`);

export const getDashboardMatches = (accountId: number, params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return fetchAPI(`/dashboard/matches/${accountId}/${query}`);
};

export const getMatchDetail = (matchId: number) =>
    fetchAPI(`/dashboard/match/${matchId}/`);

export const getDashboardHeroes = (accountId: number) =>
    fetchAPI(`/dashboard/heroes/${accountId}/`);

export const getDashboardTrends = (accountId: number, metric: string, limit = 30) =>
    fetchAPI(`/dashboard/trends/${accountId}/?metric=${metric}&limit=${limit}`);

// Heroes
export const getHeroes = () => fetchAPI('/heroes/');

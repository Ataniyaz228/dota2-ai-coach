import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenDotaClient:
    """Client for the OpenDota API with built-in rate limiting."""

    def __init__(self):
        self.base_url = settings.OPENDOTA_BASE_URL
        self.api_key = settings.OPENDOTA_API_KEY
        self.delay = settings.OPENDOTA_REQUEST_DELAY
        self.session = requests.Session()
        if self.api_key:
            self.session.params = {'api_key': self.api_key}

    def _request(self, endpoint, params=None):
        """Make a rate-limited GET request to OpenDota API."""
        url = f'{self.base_url}{endpoint}'
        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f'Rate limited. Waiting {retry_after}s...')
                time.sleep(retry_after)
                return self._request(endpoint, params)

            response.raise_for_status()
            time.sleep(self.delay)  # Rate limit pause
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f'OpenDota API error for {endpoint}: {e}')
            raise

    # =========================================================================
    # Player endpoints
    # =========================================================================

    def get_player(self, account_id):
        """GET /players/{account_id} — Profile, rank, avatar."""
        return self._request(f'/players/{account_id}')

    def get_player_matches(self, account_id, limit=50, **filters):
        """GET /players/{account_id}/matches — Match history."""
        params = {'limit': limit, **filters}
        return self._request(f'/players/{account_id}/matches', params=params)

    def get_player_heroes(self, account_id):
        """GET /players/{account_id}/heroes — Hero win/loss stats."""
        return self._request(f'/players/{account_id}/heroes')

    def get_player_totals(self, account_id):
        """GET /players/{account_id}/totals — Aggregate totals."""
        return self._request(f'/players/{account_id}/totals')

    def get_player_wl(self, account_id):
        """GET /players/{account_id}/wl — Win/Loss count."""
        return self._request(f'/players/{account_id}/wl')

    def refresh_player(self, account_id):
        """POST /players/{account_id}/refresh — Trigger data refresh on OpenDota."""
        url = f'{self.base_url}/players/{account_id}/refresh'
        try:
            response = self.session.post(url, timeout=30)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f'Failed to refresh player {account_id}: {e}')
            return False

    # =========================================================================
    # Match endpoints
    # =========================================================================

    def get_match(self, match_id):
        """GET /matches/{match_id} — Full match details."""
        return self._request(f'/matches/{match_id}')

    # =========================================================================
    # Hero & Benchmark endpoints
    # =========================================================================

    def get_heroes(self):
        """GET /heroes — Hero reference data."""
        return self._request('/heroes')

    def get_hero_benchmarks(self, hero_id):
        """GET /benchmarks?hero_id=X — Percentile benchmarks."""
        return self._request('/benchmarks', params={'hero_id': hero_id})

    # =========================================================================
    # Search
    # =========================================================================

    def search_player(self, query):
        """GET /search?q=query — Search players by name."""
        return self._request('/search', params={'q': query})

    # =========================================================================
    # Utility
    # =========================================================================

    @staticmethod
    def steam64_to_account_id(steam_id_64):
        """Convert Steam 64-bit ID to 32-bit Account ID."""
        return steam_id_64 - 76561197960265728

    @staticmethod
    def account_id_to_steam64(account_id):
        """Convert 32-bit Account ID to Steam 64-bit ID."""
        return account_id + 76561197960265728

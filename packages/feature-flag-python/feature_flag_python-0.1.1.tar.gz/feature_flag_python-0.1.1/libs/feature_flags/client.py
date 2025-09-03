"""Main feature flag client implementation."""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import requests

from .exceptions import FeatureFlagServerError, FeatureFlagTimeout
from .types import ExperimentResponse, ExperimentVariant, FeatureFlagResponse

try:
    import httpx

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    from dotenv import load_dotenv

    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


class FeatureFlagClient:
    """Client for feature flags and experiments - supports both sync and async"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 5,
        cache_ttl: int = 300,  # 5분 캐시
    ):
        self.base_url = base_url or os.getenv("FEATURE_FLAG_BASE_URL")
        if not self.base_url:
            raise ValueError("base_url or FEATURE_FLAG_BASE_URL environment variable is required")

        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: dict[str, tuple] = {}  # key: (value, expiry_time)
        self._async_client: Optional[httpx.AsyncClient] = None

    def _make_request(
        self, url: str, params: Optional[dict[str, str]] = None
    ) -> Optional[dict[str, Any]]:
        """Make sync HTTP request with error handling"""
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.warning(f"Timeout while requesting {url}")
            raise FeatureFlagTimeout(f"Request timeout for {url}") from None  # noqa: B904
        except requests.HTTPError as e:
            if e.response.status_code >= 500:
                logger.warning(f"Server error for {url}: {e}")
                raise FeatureFlagServerError(f"Server error: {e}") from e  # noqa: B904
            else:
                logger.warning(f"HTTP error for {url}: {e}")
                return None
        except requests.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None

    async def _make_async_request(
        self, url: str, params: Optional[dict[str, str]] = None
    ) -> Optional[dict[str, Any]]:
        """Make async HTTP request with error handling"""
        if not ASYNC_AVAILABLE:
            raise ImportError(
                "httpx is required for async support. Install with: pip install httpx"
            )

        try:
            if self._async_client is None:
                self._async_client = httpx.AsyncClient(timeout=self.timeout)

            response = await self._async_client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.warning(f"Async timeout while requesting {url}")
            raise FeatureFlagTimeout(f"Async request timeout for {url}") from None  # noqa: B904
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                logger.warning(f"Async server error for {url}: {e}")
                raise FeatureFlagServerError(f"Async server error: {e}") from e  # noqa: B904
            else:
                logger.warning(f"Async HTTP error for {url}: {e}")
                return None
        except httpx.RequestError as e:
            logger.warning(f"Async request failed for {url}: {e}")
            return None

    def _get_cached_or_fetch(self, cache_key: str, fetch_func) -> Any:
        """Get from cache or fetch new data (sync)"""
        now = datetime.now()

        # Check cache
        if cache_key in self._cache:
            value, expiry = self._cache[cache_key]
            if now < expiry:
                return value

        # Fetch new data
        try:
            value = fetch_func()
            if value is not None:
                self._cache[cache_key] = (value, now + timedelta(seconds=self.cache_ttl))
            return value
        except Exception as e:
            logger.error(f"Failed to fetch data for {cache_key}: {e}")
            # Return cached value if available, even if expired
            if cache_key in self._cache:
                return self._cache[cache_key][0]
            return None

    async def _get_cached_or_fetch_async(self, cache_key: str, fetch_func) -> Any:
        """Get from cache or fetch new data (async)"""
        now = datetime.now()

        # Check cache
        if cache_key in self._cache:
            value, expiry = self._cache[cache_key]
            if now < expiry:
                return value

        # Fetch new data
        try:
            value = await fetch_func()
            if value is not None:
                self._cache[cache_key] = (value, now + timedelta(seconds=self.cache_ttl))
            return value
        except Exception as e:
            logger.error(f"Failed to fetch async data for {cache_key}: {e}")
            # Return cached value if available, even if expired
            if cache_key in self._cache:
                return self._cache[cache_key][0]
            return None

    # Sync methods
    def is_feature_enabled(self, flag_id: str, default: bool = False) -> bool:
        """Check if feature flag is enabled

        Args:
            flag_id: Feature flag identifier
            default: Default value if request fails or flag not found
        """
        cache_key = f"feature:{flag_id}"

        def fetch():
            url = f"{self.base_url}/feature-flags/{flag_id}"
            data = self._make_request(url)
            if data is None:
                return None
            return data.get("enabled", default)

        result = self._get_cached_or_fetch(cache_key, fetch)
        return result if result is not None else default

    def get_feature_config(
        self, flag_id: str, default_enabled: bool = False
    ) -> FeatureFlagResponse:
        """Get feature flag with configuration"""
        cache_key = f"feature_config:{flag_id}"

        def fetch():
            url = f"{self.base_url}/feature-flags/{flag_id}"
            data = self._make_request(url)
            if data is None:
                return None

            return FeatureFlagResponse(
                enabled=data.get("enabled", default_enabled), config=data.get("config")
            )

        result = self._get_cached_or_fetch(cache_key, fetch)
        return result or FeatureFlagResponse(enabled=default_enabled)

    def get_experiment_variant(
        self,
        experiment_id: str,
        user_id: str,
        default_variant: str = ExperimentVariant.CONTROL,
    ) -> str:
        """Get experiment variant for user

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            default_variant: Default variant if request fails
        """
        cache_key = f"experiment:{experiment_id}:{user_id}"

        def fetch():
            url = f"{self.base_url}/experiments/{experiment_id}"
            params = {"userId": user_id}
            data = self._make_request(url, params)
            if data is None:
                return None

            variant = data.get("variant", default_variant)
            is_enabled = data.get("isEnabled", True)

            if not is_enabled:
                variant = default_variant
                payload = None
            else:
                payload = data.get("payload")

            return ExperimentResponse(
                id=data.get("id", experiment_id),
                variant=variant,
                isEnabled=is_enabled,
                payload=payload,
            )

        result = self._get_cached_or_fetch(cache_key, fetch)
        return result.variant if result is not None else default_variant

    def get_experiment_config(
        self,
        experiment_id: str,
        user_id: str,
        default_variant: str = ExperimentVariant.CONTROL,
    ) -> ExperimentResponse:
        """Get experiment variant with configuration"""
        cache_key = f"experiment_config:{experiment_id}:{user_id}"

        def fetch():
            url = f"{self.base_url}/experiments/{experiment_id}"
            params = {"userId": user_id}
            data = self._make_request(url, params)
            if data is None:
                return None

            variant = data.get("variant", default_variant)
            is_enabled = data.get("isEnabled", True)

            if not is_enabled:
                variant = default_variant
                payload = None
            else:
                payload = data.get("payload")

            return ExperimentResponse(
                id=data.get("id", experiment_id),
                variant=variant,
                isEnabled=is_enabled,
                payload=payload,
            )

        result = self._get_cached_or_fetch(cache_key, fetch)
        return result or ExperimentResponse(
            id=experiment_id, variant=default_variant, isEnabled=False, payload=None
        )

    # Async methods
    async def ais_feature_enabled(self, flag_id: str, default: bool = False) -> bool:
        """Check if feature flag is enabled (async)

        Args:
            flag_id: Feature flag identifier
            default: Default value if request fails or flag not found
        """
        cache_key = f"feature:{flag_id}"

        async def fetch():
            url = f"{self.base_url}/feature-flags/{flag_id}"
            data = await self._make_async_request(url)
            if data is None:
                return None
            return data.get("enabled", default)

        result = await self._get_cached_or_fetch_async(cache_key, fetch)
        return result if result is not None else default

    async def aget_feature_config(
        self, flag_id: str, default_enabled: bool = False
    ) -> FeatureFlagResponse:
        """Get feature flag with configuration (async)"""
        cache_key = f"feature_config:{flag_id}"

        async def fetch():
            url = f"{self.base_url}/feature-flags/{flag_id}"
            data = await self._make_async_request(url)
            if data is None:
                return None

            return FeatureFlagResponse(
                enabled=data.get("enabled", default_enabled), config=data.get("config")
            )

        result = await self._get_cached_or_fetch_async(cache_key, fetch)
        return result or FeatureFlagResponse(enabled=default_enabled)

    async def aget_experiment_variant(
        self,
        experiment_id: str,
        user_id: str,
        default_variant: ExperimentVariant = ExperimentVariant.CONTROL,
    ) -> ExperimentVariant:
        """Get experiment variant for user (async)

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            default_variant: Default variant if request fails
        """
        cache_key = f"experiment:{experiment_id}:{user_id}"

        async def fetch():
            url = f"{self.base_url}/experiments/{experiment_id}"
            params = {"userId": user_id}
            data = await self._make_async_request(url, params)
            if data is None:
                return None

            variant = data.get("variant", default_variant)
            is_enabled = data.get("isEnabled", True)

            if not is_enabled:
                variant = default_variant
                payload = None
            else:
                payload = data.get("payload")

            return ExperimentResponse(
                id=data.get("id", experiment_id),
                variant=variant,
                isEnabled=is_enabled,
                payload=payload,
            )

        result = await self._get_cached_or_fetch_async(cache_key, fetch)
        return result.variant if result is not None else default_variant

    async def aget_experiment_config(
        self,
        experiment_id: str,
        user_id: str,
        default_variant: str = ExperimentVariant.CONTROL,
    ) -> ExperimentResponse:
        """Get experiment variant with configuration (async)"""
        cache_key = f"experiment_config:{experiment_id}:{user_id}"

        async def fetch():
            url = f"{self.base_url}/experiments/{experiment_id}"
            params = {"userId": user_id}
            data = await self._make_async_request(url, params)
            if data is None:
                return None

            variant = data.get("variant", default_variant)
            is_enabled = data.get("isEnabled", True)

            if not is_enabled:
                variant = default_variant
                payload = None
            else:
                payload = data.get("payload")

            return ExperimentResponse(
                id=data.get("id", experiment_id),
                variant=variant,
                isEnabled=is_enabled,
                payload=payload,
            )

        result = await self._get_cached_or_fetch_async(cache_key, fetch)
        return result or ExperimentResponse(
            id=experiment_id, variant=default_variant, isEnabled=False, payload=None
        )

    async def close(self):
        """Close async client"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None


# Global client instance
_client: Optional[FeatureFlagClient] = None


def initialize_client(base_url: Optional[str] = None, **kwargs):
    """Initialize global feature flag client"""
    global _client
    _client = FeatureFlagClient(base_url=base_url, **kwargs)


def get_client() -> FeatureFlagClient:
    """Get global client instance"""
    if _client is None:
        initialize_client()
    return _client


# Sync convenience functions
def is_enabled(flag_id: str, default: bool = False) -> bool:
    """Check if feature flag is enabled

    Args:
        flag_id: Feature flag identifier
        default: Default value if request fails or flag not found
    """
    return get_client().is_feature_enabled(flag_id, default=default)


def get_feature(flag_id: str, default_enabled: bool = False) -> FeatureFlagResponse:
    """Get feature flag with config

    Args:
        flag_id: Feature flag identifier
        default_enabled: Default enabled state if request fails
    """
    return get_client().get_feature_config(flag_id, default_enabled=default_enabled)


def get_experiment(
    experiment_id: str, user_id: str, default_variant: str = ExperimentVariant.CONTROL
) -> ExperimentResponse:
    """Get experiment variant with config

    Args:
        experiment_id: Experiment identifier
        user_id: User identifier
        default_variant: Default variant if request fails
    """
    return get_client().get_experiment_config(
        experiment_id, user_id, default_variant=default_variant
    )


def get_variant(
    experiment_id: str, user_id: str, default_variant: str = ExperimentVariant.CONTROL
) -> ExperimentVariant:
    """Get experiment variant

    Args:
        experiment_id: Experiment identifier
        user_id: User identifier
        default_variant: Default variant if request fails
    """
    return get_client().get_experiment_variant(
        experiment_id, user_id, default_variant=default_variant
    )


# Async convenience functions
async def ais_enabled(flag_id: str, default: bool = False) -> bool:
    """Check if feature flag is enabled (async)

    Args:
        flag_id: Feature flag identifier
        default: Default value if request fails or flag not found
    """
    return await get_client().ais_feature_enabled(flag_id, default=default)


async def aget_feature(flag_id: str, default_enabled: bool = False) -> FeatureFlagResponse:
    """Get feature flag with config (async)

    Args:
        flag_id: Feature flag identifier
        default_enabled: Default enabled state if request fails
    """
    return await get_client().aget_feature_config(flag_id, default_enabled=default_enabled)


async def aget_experiment(
    experiment_id: str, user_id: str, default_variant: str = ExperimentVariant.CONTROL
) -> ExperimentResponse:
    """Get experiment variant with config (async)

    Args:
        experiment_id: Experiment identifier
        user_id: User identifier
        default_variant: Default variant if request fails
    """
    return await get_client().aget_experiment_config(
        experiment_id, user_id, default_variant=default_variant
    )


async def aget_variant(
    experiment_id: str, user_id: str, default_variant: str = ExperimentVariant.CONTROL
) -> ExperimentVariant:
    """Get experiment variant (async)

    Args:
        experiment_id: Experiment identifier
        user_id: User identifier
        default_variant: Default variant if request fails
    """
    return await get_client().aget_experiment_variant(
        experiment_id, user_id, default_variant=default_variant
    )


# Cleanup function for async clients
async def cleanup_async_clients():
    """Cleanup async clients - call this when shutting down"""
    global _client
    if _client:
        await _client.close()

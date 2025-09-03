"""Custom exceptions for feature flags."""


class FeatureFlagError(Exception):
    """Base exception for feature flag operations."""

    pass


class FeatureFlagTimeout(FeatureFlagError):
    """Raised when feature flag request times out."""

    pass


class FeatureFlagServerError(FeatureFlagError):
    """Raised when feature flag server returns an error."""

    pass


class FeatureFlagConfigError(FeatureFlagError):
    """Raised when feature flag configuration is invalid."""

    pass

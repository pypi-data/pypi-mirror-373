"""
Feature Flags Python Client

A unified library for feature flags and A/B testing across all services.
Supports both sync and async operations.
"""

# Global client management
from .client import (
    FeatureFlagClient,
    aget_experiment,
    aget_feature,
    aget_variant,
    # Async convenience functions
    ais_enabled,
    cleanup_async_clients,
    get_client,
    get_experiment,
    get_feature,
    get_variant,
    initialize_client,
    # Convenience functions
    is_enabled,
)
from .context_managers import (
    aexperiment_context,
    afeature_toggle,
    experiment_context,
    feature_toggle,
)
from .decorators import aexperiment_variant, afeature_flag, experiment_variant, feature_flag
from .exceptions import FeatureFlagError, FeatureFlagServerError, FeatureFlagTimeout
from .types import ExperimentResponse, ExperimentVariant, FeatureFlagResponse

__version__ = "0.1.1"
__author__ = "Jihoon Kim"
__email__ = "pigberger70@gmail.com"

__all__ = [
    # Client
    "FeatureFlagClient",
    "initialize_client",
    "get_client",
    "cleanup_async_clients",
    # Types
    "ExperimentVariant",
    "FeatureFlagResponse",
    "ExperimentResponse",
    # Sync functions
    "is_enabled",
    "get_feature",
    "get_experiment",
    "get_variant",
    # Async functions
    "ais_enabled",
    "aget_feature",
    "aget_experiment",
    "aget_variant",
    # Decorators
    "feature_flag",
    "afeature_flag",
    "experiment_variant",
    "aexperiment_variant",
    # Context managers
    "feature_toggle",
    "afeature_toggle",
    "experiment_context",
    "aexperiment_context",
    # Exceptions
    "FeatureFlagError",
    "FeatureFlagTimeout",
    "FeatureFlagServerError",
]

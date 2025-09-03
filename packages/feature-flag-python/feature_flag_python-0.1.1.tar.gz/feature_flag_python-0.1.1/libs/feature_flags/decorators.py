"""Decorators for feature flags and experiments."""

from functools import wraps
from typing import Any, Callable

from .types import ExperimentVariant


def feature_flag(flag_id: str, default: bool = False, default_return: Any = None):  # noqa: ANN201,ANN002,ANN003
    """Decorator to conditionally execute function based on feature flag

    Args:
        flag_id: Feature flag identifier
        default: Default value if request fails
        default_return: Return value if feature is disabled
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from . import is_enabled

            if is_enabled(flag_id, default=default):
                return func(*args, **kwargs)
            return default_return

        return wrapper

    return decorator


def afeature_flag(flag_id: str, default: bool = False, default_return: Any = None):  # noqa: ANN201,ANN002,ANN003
    """Async decorator to conditionally execute function based on feature flag

    Args:
        flag_id: Feature flag identifier
        default: Default value if request fails
        default_return: Return value if feature is disabled
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from . import ais_enabled

            if await ais_enabled(flag_id, default=default):
                return await func(*args, **kwargs)
            return default_return

        return wrapper

    return decorator


def experiment_variant(
    experiment_id: str,
    user_id_key: str = "user_id",
    default_variant: ExperimentVariant = ExperimentVariant.CONTROL,
):  # noqa: ANN201,ANN002,ANN003
    """Decorator to add experiment variant to function

    Args:
        experiment_id: Experiment identifier
        user_id_key: Key to extract user_id from kwargs
        default_variant: Default variant if request fails
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from . import get_variant

            # Extract user_id from kwargs
            user_id = kwargs.get(user_id_key)
            if user_id:
                variant = get_variant(experiment_id, user_id, default_variant=default_variant)
                kwargs["experiment_variant"] = variant
            return func(*args, **kwargs)

        return wrapper

    return decorator


def aexperiment_variant(
    experiment_id: str,
    user_id_key: str = "user_id",
    default_variant: ExperimentVariant = ExperimentVariant.CONTROL,
):  # noqa: ANN201,ANN002,ANN003
    """Async decorator to add experiment variant to function

    Args:
        experiment_id: Experiment identifier
        user_id_key: Key to extract user_id from kwargs
        default_variant: Default variant if request fails
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from . import aget_variant

            # Extract user_id from kwargs
            user_id = kwargs.get(user_id_key)
            if user_id:
                variant = await aget_variant(
                    experiment_id, user_id, default_variant=default_variant
                )
                kwargs["experiment_variant"] = variant
            return await func(*args, **kwargs)

        return wrapper

    return decorator

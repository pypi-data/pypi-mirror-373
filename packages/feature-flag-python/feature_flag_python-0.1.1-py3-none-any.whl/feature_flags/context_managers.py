"""Context managers for feature flags and experiments."""

from typing import Optional

from .types import ExperimentResponse, ExperimentVariant


class feature_toggle:  # noqa: ANN201,ANN202
    """Context manager for feature flag"""

    def __init__(self, flag_id: str, default: bool = False):
        self.flag_id = flag_id
        self.default = default
        self.enabled = False

    def __enter__(self) -> bool:
        from . import is_enabled

        self.enabled = is_enabled(self.flag_id, default=self.default)
        return self.enabled

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class afeature_toggle:  # noqa: ANN201,ANN202
    """Async context manager for feature flag"""

    def __init__(self, flag_id: str, default: bool = False):
        self.flag_id = flag_id
        self.default = default
        self.enabled = False

    async def __aenter__(self) -> bool:
        from . import ais_enabled

        self.enabled = await ais_enabled(self.flag_id, default=self.default)
        return self.enabled

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class experiment_context:  # noqa: ANN201,ANN202
    """Context manager for experiments"""

    def __init__(
        self,
        experiment_id: str,
        user_id: str,
        default_variant: ExperimentVariant = ExperimentVariant.CONTROL,
    ):
        self.experiment_id = experiment_id
        self.user_id = user_id
        self.default_variant = default_variant
        self.response: Optional[ExperimentResponse] = None

    def __enter__(self) -> ExperimentResponse:
        from . import get_experiment

        self.response = get_experiment(
            self.experiment_id, self.user_id, default_variant=self.default_variant
        )
        return self.response

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class aexperiment_context:  # noqa: ANN201,ANN202
    """Async context manager for experiments"""

    def __init__(
        self,
        experiment_id: str,
        user_id: str,
        default_variant: ExperimentVariant = ExperimentVariant.CONTROL,
    ):
        self.experiment_id = experiment_id
        self.user_id = user_id
        self.default_variant = default_variant
        self.response: Optional[ExperimentResponse] = None

    async def __aenter__(self) -> ExperimentResponse:
        from . import aget_experiment

        self.response = await aget_experiment(
            self.experiment_id, self.user_id, default_variant=self.default_variant
        )
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

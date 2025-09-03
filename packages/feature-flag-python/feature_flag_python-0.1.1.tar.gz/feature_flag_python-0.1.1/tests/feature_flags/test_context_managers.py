import pytest

from libs.feature_flags.context_managers import (
    aexperiment_context,
    afeature_toggle,
    experiment_context,
    feature_toggle,
)
from libs.feature_flags.types import ExperimentResponse, ExperimentVariant


@pytest.mark.parametrize("enabled", [True, False])
def test_feature_toggle(monkeypatch, enabled):
    monkeypatch.setattr("libs.feature_flags.is_enabled", lambda flag_id, default=False: enabled)
    with feature_toggle("flag", default=not enabled) as result:
        assert result is enabled


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [True, False])
async def test_afeature_toggle(monkeypatch, enabled):
    async def dummy_ais_enabled(flag_id, default=False):
        return enabled

    monkeypatch.setattr("libs.feature_flags.ais_enabled", dummy_ais_enabled)
    async with afeature_toggle("flag", default=not enabled) as result:
        assert result is enabled


def test_experiment_context(monkeypatch):
    def dummy_get_experiment(experiment_id, user_id, default_variant):
        return ExperimentResponse(
            id=experiment_id, variant=default_variant, isEnabled=True, payload=None
        )

    monkeypatch.setattr("libs.feature_flags.get_experiment", dummy_get_experiment)
    with experiment_context("exp", "user", "treatment") as resp:
        assert resp.variant == "treatment"


@pytest.mark.asyncio
async def test_aexperiment_context(monkeypatch):
    async def dummy_aget_experiment(experiment_id, user_id, default_variant):
        return ExperimentResponse(
            id=experiment_id, variant=default_variant, isEnabled=True, payload=None
        )

    monkeypatch.setattr("libs.feature_flags.aget_experiment", dummy_aget_experiment)
    async with aexperiment_context("exp", "user", ExperimentVariant.CONTROL) as resp:
        assert resp.variant == ExperimentVariant.CONTROL

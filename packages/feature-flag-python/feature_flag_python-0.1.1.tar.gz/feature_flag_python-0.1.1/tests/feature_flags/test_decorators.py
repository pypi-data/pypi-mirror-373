import pytest

from libs.feature_flags.decorators import (
    aexperiment_variant,
    afeature_flag,
    experiment_variant,
    feature_flag,
)
from libs.feature_flags.types import ExperimentVariant


@pytest.mark.parametrize("flag_enabled, expected", [(True, 1), (False, None)])
def test_feature_flag(monkeypatch, flag_enabled, expected):
    monkeypatch.setattr(
        "libs.feature_flags.is_enabled", lambda flag_id, default=False: flag_enabled
    )

    @feature_flag("flag", default=False, default_return=None)
    def func():
        return 1

    assert func() == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("flag_enabled, expected", [(True, 1), (False, None)])
async def test_afeature_flag(monkeypatch, flag_enabled, expected):
    async def dummy_ais_enabled(flag_id, default=False):
        return flag_enabled

    monkeypatch.setattr("libs.feature_flags.ais_enabled", dummy_ais_enabled)

    @afeature_flag("flag", default=False, default_return=None)
    async def func():
        return 1

    assert await func() == expected


def test_experiment_variant(monkeypatch):
    def dummy_get_variant(experiment_id, user_id, default_variant):
        return "treatment_2"

    monkeypatch.setattr("libs.feature_flags.get_variant", dummy_get_variant)

    @experiment_variant("exp", user_id_key="user_id", default_variant="treatment_2")
    def func(user_id=None, experiment_variant=None):
        return experiment_variant

    assert func(user_id="user") == "treatment_2"


@pytest.mark.asyncio
async def test_aexperiment_variant(monkeypatch):
    async def dummy_aget_variant(experiment_id, user_id, default_variant):
        return ExperimentVariant.CONTROL

    monkeypatch.setattr("libs.feature_flags.aget_variant", dummy_aget_variant)

    @aexperiment_variant("exp", user_id_key="user_id", default_variant=ExperimentVariant.CONTROL)
    async def func(user_id=None, experiment_variant=None):
        return experiment_variant

    assert await func(user_id="user") == ExperimentVariant.CONTROL

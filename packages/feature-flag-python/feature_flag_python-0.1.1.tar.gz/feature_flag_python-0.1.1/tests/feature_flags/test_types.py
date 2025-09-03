from libs.feature_flags.types import ExperimentResponse, ExperimentVariant, FeatureFlagResponse


def test_experiment_variant_constant():
    assert ExperimentVariant.CONTROL == "control"


def test_feature_flag_response():
    resp = FeatureFlagResponse(enabled=True, config={"k": 1})
    assert resp.enabled is True
    assert resp.config == {"k": 1}


def test_experiment_response():
    resp = ExperimentResponse(id="exp-ab-1", variant="treatment", isEnabled=True, payload=None)
    assert resp.variant == "treatment"
    assert resp.isEnabled is True
    assert resp.payload is None

import pytest

from libs.feature_flags.client import (
    FeatureFlagClient,
    get_client,
    get_experiment,
    get_feature,
    get_variant,
    initialize_client,
    is_enabled,
)
from libs.feature_flags.types import ExperimentResponse, ExperimentVariant, FeatureFlagResponse


class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
        self._raise = False

    def json(self):
        return self._json

    def raise_for_status(self):
        if self._raise:
            raise Exception("HTTP error")


@pytest.fixture
def client(monkeypatch):
    return FeatureFlagClient(base_url="http://localhost:9999", timeout=1, cache_ttl=1)


def test_is_feature_enabled(monkeypatch, client):
    monkeypatch.setattr(client, "_make_request", lambda url, params=None: {"enabled": True})
    assert client.is_feature_enabled("flag_a") is True
    monkeypatch.setattr(client, "_make_request", lambda url, params=None: None)
    assert client.is_feature_enabled("flag_b", default=False) is False


def test_get_feature_config(monkeypatch, client):
    monkeypatch.setattr(
        client, "_make_request", lambda url, params=None: {"enabled": False, "config": {"foo": 1}}
    )
    resp = client.get_feature_config("flag")
    assert isinstance(resp, FeatureFlagResponse)
    assert resp.enabled is False
    assert resp.config == {"foo": 1}


def test_get_experiment_config(monkeypatch, client):
    monkeypatch.setattr(
        client,
        "_make_request",
        lambda url, params=None: {"variant": "treatment", "config": {"bar": 2}},
    )
    resp = client.get_experiment_config("exp", "user")
    assert isinstance(resp, ExperimentResponse)
    assert resp.variant == "treatment"
    # assert resp.config == {"bar": 2}  # config는 더 이상 없음


def test_global_client(monkeypatch):
    initialize_client(base_url="http://localhost:9999")
    c = get_client()
    assert isinstance(c, FeatureFlagClient)


def test_is_enabled_global(monkeypatch):
    initialize_client(base_url="http://localhost:9999")
    monkeypatch.setattr(
        FeatureFlagClient, "is_feature_enabled", lambda self, flag_id, default=False: True
    )
    assert is_enabled("flag") is True


def test_get_feature_global(monkeypatch):
    initialize_client(base_url="http://localhost:9999")
    monkeypatch.setattr(
        FeatureFlagClient,
        "get_feature_config",
        lambda self, flag_id, default_enabled=False: FeatureFlagResponse(enabled=True, config=None),
    )
    resp = get_feature("flag")
    assert resp.enabled is True


def test_get_experiment_global(monkeypatch):
    initialize_client(base_url="http://localhost:9999")
    monkeypatch.setattr(
        FeatureFlagClient,
        "get_experiment_config",
        lambda self, exp_id, user_id, default_variant=ExperimentVariant.CONTROL: ExperimentResponse(
            id=exp_id, variant="treatment", isEnabled=True, payload=None
        ),
    )
    resp = get_experiment("exp", "user")
    assert resp.variant == "treatment"


def test_get_variant_global(monkeypatch):
    initialize_client(base_url="http://localhost:9999")
    monkeypatch.setattr(
        FeatureFlagClient,
        "get_experiment_variant",
        lambda self, exp_id, user_id, default_variant=ExperimentVariant.CONTROL: "treatment",
    )
    resp = get_variant("exp", "user")
    assert resp == "treatment"


def test_client_init_env(monkeypatch):
    monkeypatch.setenv("FEATURE_FLAG_BASE_URL", "http://env-url")
    c = FeatureFlagClient()
    assert c.base_url == "http://env-url"
    monkeypatch.delenv("FEATURE_FLAG_BASE_URL")
    with pytest.raises(ValueError):
        FeatureFlagClient()

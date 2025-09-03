import pytest

from libs.feature_flags.exceptions import (
    FeatureFlagConfigError,
    FeatureFlagError,
    FeatureFlagServerError,
    FeatureFlagTimeout,
)


def test_feature_flag_error():
    with pytest.raises(FeatureFlagError):
        raise FeatureFlagError()


def test_feature_flag_timeout():
    with pytest.raises(FeatureFlagTimeout):
        raise FeatureFlagTimeout()


def test_feature_flag_server_error():
    with pytest.raises(FeatureFlagServerError):
        raise FeatureFlagServerError()


def test_feature_flag_config_error():
    with pytest.raises(FeatureFlagConfigError):
        raise FeatureFlagConfigError()

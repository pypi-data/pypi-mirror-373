"""Test Providers and the AppConfig objects."""

import inspect

import pytest

from regscale.models import config


def test_Provider():
    """Test the Provider class"""
    results = config.Provider(provider="fake_provider")
    assert results.provider == "fake_provider"
    results.__setitem__("key", "value")
    assert results.key == "value"
    with pytest.raises(NotImplementedError):
        results.refresh()


def test_provider_class_creation():
    """Test that the provider classes are created."""
    providers = list(config.providers.keys())
    # Get a list of all classes in the module
    all_classes = [name for name, obj in inspect.getmembers(config) if inspect.isclass(obj)]
    for provider in providers:
        assert provider in all_classes, f"{provider} is not defined"

"""Tests for environment-backed application settings."""

import pytest

from app.core.config import Settings


def test_default_policy_settings() -> None:
    settings = Settings()

    assert settings.max_purchase_paise == 500_000
    assert settings.approval_threshold_paise == 200_000
    assert settings.allowed_merchant_ids == frozenset({"merchant-123"})


def test_policy_settings_load_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("TRUSTRAIL_MAX_PURCHASE_PAISE", "800000")
    monkeypatch.setenv("TRUSTRAIL_APPROVAL_THRESHOLD_PAISE", "300000")
    monkeypatch.setenv("TRUSTRAIL_ALLOWED_MERCHANT_IDS", "merchant-123, merchant-456")

    settings = Settings.from_environment()

    assert settings.max_purchase_paise == 800_000
    assert settings.approval_threshold_paise == 300_000
    assert settings.allowed_merchant_ids == frozenset({"merchant-123", "merchant-456"})


@pytest.mark.parametrize(
    ("max_purchase", "threshold"),
    [
        (0, 0),
        (-1, 0),
        (100, -1),
        (100, 101),
    ],
)
def test_invalid_policy_settings_are_rejected(
    max_purchase: int,
    threshold: int,
) -> None:
    with pytest.raises(ValueError):
        Settings(
            max_purchase_paise=max_purchase,
            approval_threshold_paise=threshold,
        )

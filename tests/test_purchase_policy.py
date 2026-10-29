"""Tests for purchase snapshots and deterministic policy evaluation."""

import pytest
from pydantic import ValidationError

from app.domain.purchase import (
    PurchaseIntent,
    PurchasePolicy,
    evaluate_purchase,
)


@pytest.fixture
def intent() -> PurchaseIntent:
    return PurchaseIntent(
        merchant_id="merchant-123",
        merchant_name="Example Store",
        item_id="item-456",
        item_name="Wireless Mouse",
        quantity=2,
        unit_price_paise=75000,
    )


@pytest.fixture
def policy() -> PurchasePolicy:
    return PurchasePolicy(
        max_purchase_paise=500000,
        approval_threshold_paise=200000,
        allowed_merchant_ids=frozenset({"merchant-123"}),
    )


def test_total_is_calculated_in_integer_paise(intent: PurchaseIntent) -> None:
    assert intent.total_paise == 150000


def test_snapshot_is_deterministic(intent: PurchaseIntent) -> None:
    equivalent = PurchaseIntent(**intent.model_dump())

    assert intent.canonical_snapshot_json() == equivalent.canonical_snapshot_json()
    assert intent.snapshot_hash() == equivalent.snapshot_hash()
    assert len(intent.snapshot_hash()) == 64


def test_material_change_changes_snapshot_hash(intent: PurchaseIntent) -> None:
    changed = PurchaseIntent(**{**intent.model_dump(), "unit_price_paise": 80000})

    assert intent.snapshot_hash() != changed.snapshot_hash()


def test_invalid_quantity_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PurchaseIntent(
            merchant_id="m1",
            merchant_name="Store",
            item_id="i1",
            item_name="Item",
            quantity=0,
            unit_price_paise=100,
        )


def test_fractional_price_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PurchaseIntent(
            merchant_id="m1",
            merchant_name="Store",
            item_id="i1",
            item_name="Item",
            quantity=1,
            unit_price_paise=10.5,
        )


def test_purchase_below_approval_threshold_is_allowed(
    intent: PurchaseIntent,
    policy: PurchasePolicy,
) -> None:
    small_purchase = PurchaseIntent(
        **{
            **intent.model_dump(),
            "quantity": 1,
            "unit_price_paise": 50000,
        }
    )

    decision = evaluate_purchase(small_purchase, policy)

    assert decision.status == "ALLOW"


def test_purchase_at_approval_threshold_requires_approval(
    intent: PurchaseIntent,
    policy: PurchasePolicy,
) -> None:
    at_threshold = PurchaseIntent(
        **{
            **intent.model_dump(),
            "quantity": 1,
            "unit_price_paise": 200000,
        }
    )

    decision = evaluate_purchase(at_threshold, policy)

    assert decision.status == "REQUIRE_APPROVAL"
    assert "HUMAN_APPROVAL_REQUIRED" in decision.reasons


def test_purchase_above_maximum_is_denied(
    intent: PurchaseIntent,
    policy: PurchasePolicy,
) -> None:
    too_expensive = PurchaseIntent(
        **{
            **intent.model_dump(),
            "quantity": 1,
            "unit_price_paise": 500001,
        }
    )

    decision = evaluate_purchase(too_expensive, policy)

    assert decision.status == "DENY"
    assert decision.reasons == ("PURCHASE_LIMIT_EXCEEDED",)


def test_unapproved_merchant_is_denied(
    intent: PurchaseIntent,
    policy: PurchasePolicy,
) -> None:
    other_merchant = PurchaseIntent(**{**intent.model_dump(), "merchant_id": "merchant-evil"})

    decision = evaluate_purchase(other_merchant, policy)

    assert decision.status == "DENY"
    assert decision.reasons == ("MERCHANT_NOT_ALLOWED",)


def test_purchase_exactly_at_maximum_is_not_denied(
    intent: PurchaseIntent,
    policy: PurchasePolicy,
) -> None:
    at_maximum = PurchaseIntent(
        **{
            **intent.model_dump(),
            "quantity": 1,
            "unit_price_paise": 500000,
        }
    )

    decision = evaluate_purchase(at_maximum, policy)

    assert decision.status == "REQUIRE_APPROVAL"

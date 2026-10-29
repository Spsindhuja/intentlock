"""Tests for persistent purchase and approval model definitions."""

from app.core.models import Base, PurchaseApprovalRecord, PurchaseIntentRecord


def test_purchase_tables_are_registered() -> None:
    assert "purchase_intents" in Base.metadata.tables
    assert "purchase_approvals" in Base.metadata.tables


def test_purchase_intent_has_snapshot_and_policy_fields() -> None:
    columns = PurchaseIntentRecord.__table__.columns

    assert "snapshot_hash" in columns
    assert "policy_status" in columns
    assert "total_paise" in columns
    assert columns["snapshot_hash"].nullable is False


def test_approval_has_snapshot_expiry_and_usage_fields() -> None:
    columns = PurchaseApprovalRecord.__table__.columns

    assert "purchase_intent_id" in columns
    assert "snapshot_hash" in columns
    assert "expires_at" in columns
    assert "used_at" in columns
    assert columns["snapshot_hash"].nullable is False

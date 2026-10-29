"""API tests for purchase evaluation."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PURCHASE = {
    "merchant_id": "merchant-123",
    "merchant_name": "Example Store",
    "item_id": "item-456",
    "item_name": "Wireless Mouse",
    "quantity": 1,
    "unit_price_paise": 50000,
}


def test_evaluate_purchase_returns_allow_for_small_purchase() -> None:
    response = client.post(
        "/api/v1/purchases/evaluate",
        json=VALID_PURCHASE,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["status"] == "ALLOW"
    assert body["total_paise"] == 50000
    assert body["currency"] == "INR"
    assert len(body["snapshot_hash"]) == 64


def test_evaluate_purchase_requires_approval_at_threshold() -> None:
    purchase = {**VALID_PURCHASE, "unit_price_paise": 200000}

    response = client.post("/api/v1/purchases/evaluate", json=purchase)

    assert response.status_code == 200
    assert response.json()["decision"]["status"] == "REQUIRE_APPROVAL"


def test_evaluate_purchase_denies_amount_above_limit() -> None:
    purchase = {**VALID_PURCHASE, "unit_price_paise": 500001}

    response = client.post("/api/v1/purchases/evaluate", json=purchase)

    assert response.status_code == 200
    assert response.json()["decision"]["status"] == "DENY"


def test_evaluate_purchase_denies_unapproved_merchant() -> None:
    purchase = {**VALID_PURCHASE, "merchant_id": "merchant-evil"}

    response = client.post("/api/v1/purchases/evaluate", json=purchase)

    assert response.status_code == 200
    assert response.json()["decision"]["status"] == "DENY"
    assert response.json()["decision"]["reasons"] == ["MERCHANT_NOT_ALLOWED"]


def test_evaluate_purchase_rejects_fractional_price() -> None:
    purchase = {**VALID_PURCHASE, "unit_price_paise": 10.5}

    response = client.post("/api/v1/purchases/evaluate", json=purchase)

    assert response.status_code == 422


def test_evaluate_purchase_rejects_unknown_policy_fields() -> None:
    purchase = {**VALID_PURCHASE, "max_purchase_paise": 999999999}

    response = client.post("/api/v1/purchases/evaluate", json=purchase)

    assert response.status_code == 422


def test_evaluate_purchase_rejects_zero_quantity() -> None:
    purchase = {**VALID_PURCHASE, "quantity": 0}

    response = client.post("/api/v1/purchases/evaluate", json=purchase)

    assert response.status_code == 422

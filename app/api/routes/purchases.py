"""HTTP endpoints for purchase policy evaluation."""

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings
from app.domain.purchase import (
    PolicyDecision,
    PurchaseIntent,
    PurchasePolicy,
    evaluate_purchase,
)

router = APIRouter(prefix="/api/v1/purchases", tags=["purchases"])

# Server-controlled policy loaded from validated environment settings.
DEFAULT_POLICY = PurchasePolicy(
    max_purchase_paise=settings.max_purchase_paise,
    approval_threshold_paise=settings.approval_threshold_paise,
    allowed_merchant_ids=settings.allowed_merchant_ids,
)


class PurchaseEvaluationRequest(BaseModel):
    """Purchase details supplied by the caller."""

    model_config = ConfigDict(extra="forbid")

    merchant_id: str = Field(min_length=1, max_length=100)
    merchant_name: str = Field(min_length=1, max_length=200)
    item_id: str = Field(min_length=1, max_length=100)
    item_name: str = Field(min_length=1, max_length=300)
    quantity: int = Field(strict=True, gt=0, le=1000)
    unit_price_paise: int = Field(strict=True, ge=0)


class PurchaseEvaluationResponse(BaseModel):
    """Deterministic policy evaluation result."""

    decision: PolicyDecision
    total_paise: int
    currency: str
    snapshot_hash: str


@router.post(
    "/evaluate",
    response_model=PurchaseEvaluationResponse,
)
def evaluate_purchase_endpoint(
    request: PurchaseEvaluationRequest,
) -> PurchaseEvaluationResponse:
    """Evaluate a purchase without authorizing or executing payment."""
    intent = PurchaseIntent(**request.model_dump())
    decision = evaluate_purchase(intent, DEFAULT_POLICY)

    return PurchaseEvaluationResponse(
        decision=decision,
        total_paise=intent.total_paise,
        currency=intent.currency,
        snapshot_hash=intent.snapshot_hash(),
    )

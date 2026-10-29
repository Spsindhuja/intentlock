"""Purchase intent, canonical snapshots, and deterministic authorization policy."""

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseIntent(BaseModel):
    """A proposed purchase; creating one does not authorize payment."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    merchant_id: str = Field(min_length=1, max_length=100)
    merchant_name: str = Field(min_length=1, max_length=200)
    item_id: str = Field(min_length=1, max_length=100)
    item_name: str = Field(min_length=1, max_length=300)
    quantity: int = Field(strict=True, gt=0, le=1000)
    unit_price_paise: int = Field(strict=True, ge=0)
    currency: Literal["INR"] = "INR"

    @property
    def total_paise(self) -> int:
        """Return the exact total in paise."""
        return self.quantity * self.unit_price_paise

    def canonical_snapshot(self) -> dict[str, str | int]:
        """Return the complete, stable set of purchase details to approve."""
        return {
            "schema_version": 1,
            "merchant_id": self.merchant_id,
            "merchant_name": self.merchant_name,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "unit_price_paise": self.unit_price_paise,
            "total_paise": self.total_paise,
            "currency": self.currency,
        }

    def canonical_snapshot_json(self) -> str:
        """Serialize the snapshot deterministically."""
        return json.dumps(
            self.canonical_snapshot(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def snapshot_hash(self) -> str:
        """Return the SHA-256 digest of the canonical snapshot."""
        return hashlib.sha256(self.canonical_snapshot_json().encode("utf-8")).hexdigest()


class PurchasePolicy(BaseModel):
    """Server-controlled policy limits; never accept these from an AI agent."""

    model_config = ConfigDict(frozen=True)

    max_purchase_paise: int = Field(strict=True, gt=0)
    approval_threshold_paise: int = Field(strict=True, ge=0)
    allowed_merchant_ids: frozenset[str] | None = None


class PolicyDecision(BaseModel):
    """Deterministic policy outcome for a purchase intent."""

    status: Literal["ALLOW", "REQUIRE_APPROVAL", "DENY"]
    reasons: tuple[str, ...]


def evaluate_purchase(
    intent: PurchaseIntent,
    policy: PurchasePolicy,
) -> PolicyDecision:
    """Evaluate a purchase using backend policy, independently of any LLM."""
    reasons: list[str] = []

    if (
        policy.allowed_merchant_ids is not None
        and intent.merchant_id not in policy.allowed_merchant_ids
    ):
        return PolicyDecision(
            status="DENY",
            reasons=("MERCHANT_NOT_ALLOWED",),
        )

    if intent.total_paise > policy.max_purchase_paise:
        return PolicyDecision(
            status="DENY",
            reasons=("PURCHASE_LIMIT_EXCEEDED",),
        )

    if intent.total_paise >= policy.approval_threshold_paise:
        reasons.append("HUMAN_APPROVAL_REQUIRED")

    if reasons:
        return PolicyDecision(status="REQUIRE_APPROVAL", reasons=tuple(reasons))

    return PolicyDecision(status="ALLOW", reasons=("WITHIN_POLICY_LIMITS",))

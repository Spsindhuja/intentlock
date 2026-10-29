"""Environment-backed application settings without implicit .env loading."""

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = "TrustRail API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./trustrail.db"

    max_purchase_paise: int = 500_000
    approval_threshold_paise: int = 200_000
    allowed_merchant_ids: frozenset[str] = frozenset({"merchant-123"})

    def __post_init__(self) -> None:
        """Reject invalid purchase-policy configuration at startup."""
        if self.max_purchase_paise <= 0:
            raise ValueError("Maximum purchase amount must be positive.")

        if self.approval_threshold_paise < 0:
            raise ValueError("Approval threshold cannot be negative.")

        if self.approval_threshold_paise > self.max_purchase_paise:
            raise ValueError("Approval threshold cannot exceed the maximum purchase amount.")

        if any(not merchant_id for merchant_id in self.allowed_merchant_ids):
            raise ValueError("Merchant IDs cannot be empty.")

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build validated settings from environment variables."""
        allowed_merchants = os.getenv("TRUSTRAIL_ALLOWED_MERCHANT_IDS", "merchant-123")
        merchant_ids = frozenset(
            merchant.strip() for merchant in allowed_merchants.split(",") if merchant.strip()
        )

        return cls(
            app_name=os.getenv("TRUSTRAIL_APP_NAME", "TrustRail API"),
            environment=os.getenv("TRUSTRAIL_ENVIRONMENT", "development"),
            api_prefix=os.getenv("TRUSTRAIL_API_PREFIX", "/api/v1"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./trustrail.db"),
            max_purchase_paise=int(os.getenv("TRUSTRAIL_MAX_PURCHASE_PAISE", "500000")),
            approval_threshold_paise=int(os.getenv("TRUSTRAIL_APPROVAL_THRESHOLD_PAISE", "200000")),
            allowed_merchant_ids=merchant_ids,
        )


settings = Settings.from_environment()

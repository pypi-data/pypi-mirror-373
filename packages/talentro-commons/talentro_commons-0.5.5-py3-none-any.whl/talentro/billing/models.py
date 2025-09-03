from uuid import UUID

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field

from ..general.models import BaseModel


class BillingModel(BaseModel):
    pass


class BillingOrganizationModel(BillingModel):
    organization: UUID = Field(index=True)


class BillingEvent(SQLModel, table=True):
    id: int = Field(
        primary_key=True,
    )

    organization: UUID = Field(index=True)
    event_time: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sku: str = Field(nullable=False)
    count: int = Field(nullable=False, default=1)


class BillingProfile(BillingOrganizationModel, table=True):
    stripe_customer_id: str = Field(nullable=False)

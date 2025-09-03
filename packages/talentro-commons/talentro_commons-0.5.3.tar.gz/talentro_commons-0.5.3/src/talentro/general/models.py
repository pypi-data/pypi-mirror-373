from uuid import UUID, uuid4

from typing import Optional

from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {"onupdate": lambda: datetime.now(timezone.utc)}
    )

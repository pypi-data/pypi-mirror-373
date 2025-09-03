from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .models import Link as LinkModel, Integration as IntegrationModel
from ..general.dataclasses import ResolvableModel, ResolvableCompanyModel
from talentro.services.clients import MSClient


# Integration object
class IntegrationInfo(ResolvableModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    icon: str
    type: str
    tag: Optional[str]
    description: str

    @staticmethod
    async def resolve_object(object_id: UUID) -> "IntegrationInfo | None":
        result = await MSClient.integrations().get(f"integrations/{object_id}/resolve")

        if result.status_code != 200:
            return None

        return IntegrationInfo(**result.json())

    @classmethod
    async def from_model(cls: "IntegrationInfo", model: IntegrationModel) -> "IntegrationInfo":
        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            icon=model.icon,
            type=model.type,
            tag=model.tag,
            description=model.description,
        )


class IntegrationConfig(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name: str
    icon: str
    type: str
    tag: str | None
    enabled: bool | None
    description: str | None
    code_reference: str
    setup_config: dict
    order: int

    @classmethod
    async def from_model(cls: "IntegrationConfig", model: IntegrationModel) -> "IntegrationConfig":
        return cls(**model.model_dump())


# Link object
class LinkInfo(ResolvableCompanyModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    integration: IntegrationInfo | None

    @staticmethod
    async def resolve_object(object_id: UUID, organization_id: UUID) -> "LinkInfo | None":
        result = await MSClient.integrations().get(f"links/{object_id}/resolve", headers={"X-Organization-ID": str(organization_id)})

        if result.status_code != 200:
            return None

        return LinkInfo(**result.json())

    @classmethod
    async def from_model(cls: "LinkInfo", model: LinkModel) -> "LinkInfo | None":
        integration = await IntegrationInfo.resolve_object(model.integration_id)

        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            status=model.status,
            integration=integration,
        )


class LinkConfig(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    auth_config: dict
    integration_id: UUID

    @classmethod
    async def from_model(cls: "LinkConfig", model: LinkModel) -> "LinkConfig":
        return cls(**model.model_dump())
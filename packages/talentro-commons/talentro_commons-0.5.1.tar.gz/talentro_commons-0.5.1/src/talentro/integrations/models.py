from uuid import UUID

from sqlalchemy import Column, JSON
from sqlmodel import Field

from ..general.models import BaseModel


class IntegrationsModel(BaseModel):
    pass


class IntegrationsOrganizationModel(IntegrationsModel):
    organization: UUID = Field(index=True)



class Integration(IntegrationsModel, table=True):
    name: str = Field(index=True)
    icon: str = Field(index=True)
    type: str = Field(index=True)
    tag: str = Field(index=True, nullable=True)
    enabled: bool = Field(default=True, nullable=True)
    description: str = Field(index=True, nullable=True)
    code_reference: str = Field(index=True)
    setup_config: dict = Field(sa_column=Column(JSON))
    order: int = Field(default=0)


class Link(IntegrationsOrganizationModel, table=True):
    name: str = Field(index=True)
    status: str = Field(index=True)
    auth_config: dict = Field(sa_column=Column(JSON))
    integration_id: UUID = Field(foreign_key="integration.id")

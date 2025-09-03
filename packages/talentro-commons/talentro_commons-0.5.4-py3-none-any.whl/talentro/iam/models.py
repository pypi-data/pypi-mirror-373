from uuid import UUID

from sqlmodel import Field
from sqlalchemy import Column, JSON

from ..general.models import BaseModel


class IAMModel(BaseModel):
    pass


class IAMOrganizationModel(BaseModel):
    organization: UUID = Field(index=True)


class CompositeRole(IAMModel, table=True):
    name: str = Field(index=True)
    roles: list = Field(sa_column=Column(JSON))
    organization: UUID = Field(index=True, nullable=True)
    manageable_roles: list = Field(sa_column=Column(JSON))
    permission_level: int = Field(default=0)


class MemberRoleConnection(IAMOrganizationModel, table=True):
    composite_role_id: UUID = Field(foreign_key="compositerole.id")
    member: UUID = Field(index=True, nullable=False)

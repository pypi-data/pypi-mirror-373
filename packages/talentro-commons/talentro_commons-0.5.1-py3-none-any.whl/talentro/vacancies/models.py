from enum import StrEnum
from uuid import UUID

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON, UniqueConstraint, Enum
from sqlmodel import Field

from ..general.models import BaseModel


class SalaryFrequency(StrEnum):
    MONTH = "month"
    YEAR = "year"
    WEEK = "week"
    HOUR = "hour"

class RemoteType(StrEnum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"

class SourceType(StrEnum):
    ATS = "ats"
    CUSTOM_FILE = "custom-file"


class VacanciesModel(BaseModel):
    pass


class VacanciesOrganizationModel(VacanciesModel):
    organization: UUID = Field(index=True)


class Feed(VacanciesOrganizationModel, table=True):
    name: str = Field(index=True)
    status: str = Field(index=True)
    file_url: Optional[str] = Field()
    ats_link_id: Optional[UUID] = Field()
    last_sync_date: Optional[datetime] = Field()
    source_type: SourceType =  Field(sa_column=Column(Enum(SourceType)))
    synced_vacancy_count: int = Field(default=0)
    mapping: list = Field(sa_column=Column(JSON))
    custom_fields: list = Field(sa_column=Column(JSON))


class Vacancy(VacanciesOrganizationModel, table=True):
    feed_id: UUID = Field(foreign_key="feed.id")
    reference_number: str = Field(index=True)
    requisition_id: str = Field(index=True)
    title: str = Field(index=True)
    description: str = Field()
    status: str = Field()
    job_site_url: str = Field()
    company_name: str = Field(index=True)
    parent_company_name: Optional[str] = Field()
    remote_type: Optional[RemoteType] = Field(sa_column=Column(Enum(RemoteType)))
    publish_date: Optional[datetime] = Field()
    expiration_date: Optional[datetime] = Field()
    last_updated_date: Optional[datetime] = Field()
    category: List[str] = Field(sa_column=Column(JSON))
    experience: List[str] = Field(sa_column=Column(JSON))
    education: List[str] = Field(sa_column=Column(JSON))
    hours_fte: Optional[float] = Field(default=1.0)
    hours_min: Optional[int] = Field(default=1)
    hours_max: Optional[int] = Field(default=40)
    location_address: Optional[str] = Field()
    location_zipcode: Optional[str] = Field()
    location_city: Optional[str] = Field()
    location_state: Optional[str] = Field()
    location_country: Optional[str] = Field()
    salary_min: Optional[float] = Field()
    salary_max: Optional[float] = Field()
    salary_currency: str = Field(default="EUR")
    salary_frequency: SalaryFrequency = Field(sa_column=Column(Enum(SalaryFrequency)))
    recruiter_first_name: Optional[str] = Field()
    recruiter_last_name: Optional[str] = Field()
    recruiter_phone_number: Optional[str] = Field()
    recruiter_email: Optional[str] = Field()
    recruiter_role: Optional[str] = Field()
    checksum: str = Field(index=True)

    __table_args__ = (
        UniqueConstraint("feed_id", "reference_number", name="uq_feed_reference"),
    )


class Modification(VacanciesOrganizationModel, table=True):
    name: str = Field(index=True)
    type: str = Field(index=True)
    selector_configuration: dict = Field(sa_column=Column(JSON))
    changes_configuration: dict = Field(sa_column=Column(JSON))


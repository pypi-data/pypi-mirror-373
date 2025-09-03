import os

from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID
from dataclasses import field
from pydantic.dataclasses import dataclass

from httpx import AsyncClient
from pydantic import BaseModel

from ..general.dataclasses import ResolvableCompanyModel
from ..integrations.dataclasses import LinkInfo
from ..util.enum import to_enum
from ..vacancies.models import Feed as FeedModel, Vacancy as VacancyModel, SalaryFrequency, RemoteType
from ..util.vacancy import generate_vacancy_hash

class VacancyLocation(BaseModel):
    zip_code: str | None = None
    city: str | None = None
    address: str | None = None
    state: str | None = None
    country: str | None = None


class Salary(BaseModel):
    min: float | None = None
    max: float | None = None
    currency: str = "EUR"
    frequency: SalaryFrequency = "month"


class Hours(BaseModel):
    min: int = 0
    max: int = 40
    fte: float = 1.0


class ContactDetails(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    role: str | None = None


class VacancyData(BaseModel):

    # Required fields
    reference_number: str
    requisition_id: str
    title: str
    description: str
    job_site_url: str
    company_name: str
    publish_date: datetime | None = None
    category: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)

    # Connected data
    hours: Hours = field(default_factory=Hours)
    location: VacancyLocation = field(default_factory=VacancyLocation)
    salary: Salary = field(default_factory=Salary)
    recruiter: ContactDetails = field(default_factory=ContactDetails)

    # Optional fields
    status: str | None = None
    parent_company_name: str | None = None
    remote_type: RemoteType | None = None
    expiration_date: datetime | None = None
    last_updated_date: datetime | None = None

    def to_model(self, feed: FeedModel):
        model = VacancyModel(
            feed_id=feed.id,
            organization=feed.organization,
            reference_number=self.reference_number,
            requisition_id=self.requisition_id,
            title=self.title,
            description=self.description,
            status=self.status,
            job_site_url=self.job_site_url,
            company_name=self.company_name,
            parent_company_name=self.parent_company_name,
            remote_type=self.remote_type.value if self.remote_type else None,
            publish_date=self.publish_date,
            expiration_date=self.expiration_date,
            last_updated_date=self.last_updated_date,
            category=self.category,
            experience=self.experience,
            education=self.education,
            hours_fte=self.hours.fte,
            hours_min=self.hours.min,
            hours_max=self.hours.max,
            location_address=self.location.address,
            location_zipcode=self.location.zip_code,
            location_city=self.location.city,
            location_state=self.location.state,
            location_country=self.location.country,
            salary_min=self.salary.min,
            salary_max=self.salary.max,
            salary_currency=self.salary.currency,
            salary_frequency=self.salary.frequency.value if self.salary.frequency else SalaryFrequency.MONTH,
            recruiter_first_name=self.recruiter.first_name,
            recruiter_last_name=self.recruiter.last_name,
            recruiter_phone_number=self.recruiter.phone_number,
            recruiter_email=self.recruiter.email,
            recruiter_role=self.recruiter.role,
        )

        checksum = generate_vacancy_hash(model)
        model.checksum = checksum
        return model


class Vacancy(VacancyData):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID
    feed_id: UUID

    @classmethod
    async def from_model(cls: "Vacancy", model: VacancyModel) -> "Vacancy":
        hours = Hours(
            min=model.hours_min,
            max=model.hours_max,
            fte=model.hours_fte,
        )

        location = VacancyLocation(
            address=getattr(model, "location_address", None),
            zip_code=getattr(model, "location_zipcode", None),
            city=getattr(model, "location_city", None),
            state=getattr(model, "location_state", None),
            country=getattr(model, "location_country", None),
        )

        salary = Salary(
            min=getattr(model, "salary_min", None),
            max=getattr(model, "salary_max", None),
            currency=getattr(model, "salary_currency", "EUR") or "EUR",
            frequency=to_enum(SalaryFrequency, getattr(model, "salary_frequency", SalaryFrequency.MONTH) or SalaryFrequency.MONTH),
        )

        recruiter = ContactDetails(
            first_name=getattr(model, "recruiter_first_name", None),
            last_name=getattr(model, "recruiter_last_name", None),
            phone_number=getattr(model, "recruiter_phone_number", None),
            email=getattr(model, "recruiter_email", None),
            role=getattr(model, "recruiter_role", None),
        )

        remote_type = to_enum(RemoteType, getattr(model, "remote_type", None))

        return cls(
            organization=model.organization,
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            feed_id=model.feed_id,

            reference_number=model.reference_number,
            requisition_id=model.requisition_id,
            title=model.title,
            description=model.description,
            job_site_url=model.job_site_url,
            company_name=model.company_name,
            publish_date=model.publish_date,
            category=list(model.category or []),
            experience=list(model.experience or []),
            education=list(model.education or []),

            hours=hours,
            location=location,
            salary=salary,
            recruiter=recruiter,

            status=model.status,
            parent_company_name=model.parent_company_name,
            remote_type=remote_type,
            expiration_date=model.expiration_date,
            last_updated_date=model.last_updated_date,
        )

# Feed object
@dataclass
class CustomMappingValue:
    key: str
    field: str
    regex: str


@dataclass
class CustomMapping:
    return_pattern: str
    values: List[CustomMappingValue]


@dataclass
class Mapping:
    field: str
    value: str | None = None
    default: str | None = None
    custom_mapping: CustomMapping | None = None
    type: Literal['mapped' | 'custom']


class FeedInfo(ResolvableCompanyModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    file_url: Optional[str]
    ats_link: Optional[LinkInfo]
    source_type: str
    last_sync_date: Optional[datetime]
    synced_vacancy_count: int
    mapping: List[Mapping]
    custom_fields: List[Mapping]

    @staticmethod
    async def resolve_object(object_id: UUID, organization_id: UUID) -> "FeedInfo | None":
        result = await ResolveClient.vacancies().get(f"feeds/{object_id}/resolve", headers={"X-Organization-ID": str(organization_id)})

        if result.status_code != 200:
            return None

        return FeedInfo(**result.json())

    @classmethod
    async def from_model(cls: "FeedInfo", model: FeedModel) -> "FeedInfo":
        ats_link = await LinkInfo.resolve_object(model.ats_link_id, model.organization) if model.ats_link_id else None

        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            status=model.status,
            file_url=model.file_url,
            ats_link=ats_link,
            source_type=model.source_type,
            last_sync_date=model.last_sync_date,
            synced_vacancy_count=model.synced_vacancy_count,
            mapping=model.mapping,
            custom_fields=model.custom_fields,
        )


class FeedConfig(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    status: str
    file_url: Optional[str]
    source_type: str
    ats_link_id: Optional[UUID]
    last_sync_date: Optional[datetime]
    synced_vacancy_count: int
    mapping: List[Mapping]
    custom_fields: List[Mapping]

    @classmethod
    async def from_model(cls: "FeedConfig", model: FeedModel) -> "FeedConfig":
        return cls(**model.model_dump())

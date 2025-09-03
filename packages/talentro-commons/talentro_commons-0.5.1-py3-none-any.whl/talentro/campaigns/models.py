import enum

from uuid import UUID

from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column, JSON, Enum
from sqlmodel import Field

from ..general.models import BaseModel


class ChannelType(StrEnum):
    JOB_BOARD = 'job-board'
    SOCIAL = 'social'


class CampaignGoal(enum.Enum):
    REACH = 'reach'
    TRAFFIC = 'traffic'
    CONVERSION = 'conversion'
    LEADS = 'leads'


class CampaignsModel(BaseModel):
    pass


class CampaignsOrganizationModel(CampaignsModel):
    organization: UUID = Field(index=True)


class Campaign(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    status: str = Field(index=True)
    last_sync_date: Optional[datetime] = Field()
    ad_count: int = Field(default=0)
    channel_id: UUID = Field(index=True)
    channel_type: ChannelType = Field(sa_column=Column(Enum(ChannelType)))
    campaign_goal: Optional[CampaignGoal] = Field(sa_column=Column(Enum(CampaignGoal)))


class VacancySelection(CampaignsOrganizationModel, table=True):
    campaign_id: UUID = Field(foreign_key="campaign.id")
    feed_id: UUID = Field(index=True)
    selection_criteria: dict = Field(sa_column=Column(JSON))


class AdSet(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    campaign_id: UUID = Field(foreign_key="campaign.id")
    platforms: list = Field(sa_column=Column(JSON))
    ad_types: list = Field(sa_column=Column(JSON))
    settings: dict = Field(sa_column=Column(JSON))


class TargetLocation(CampaignsOrganizationModel, table=True):
    ad_set: UUID = Field(foreign_key="adset.id")
    address: str = Field(index=True)
    distance: int = Field(index=True)


class TargetAudience(CampaignsOrganizationModel, table=True):
    ad_set: UUID = Field(foreign_key="adset.id")
    age_min: int = Field(index=True, default=18)
    age_max: int = Field(index=True, default=150)
    interests: list = Field(sa_column=Column(JSON))
    languages: list = Field(sa_column=Column(JSON))


class Ad(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    campaign_id: UUID = Field(foreign_key="campaign.id")
    ad_set_id: Optional[UUID] = Field(foreign_key="adset.id")
    vacancy_id: Optional[UUID] = Field()
    lead_form: Optional[UUID] = Field(foreign_key="leadform.id")
    primary_text: str = Field()
    title: str = Field()
    description: Optional[str] = Field()
    conversion_goal: Optional[str] = Field()


class LeadForm(CampaignsOrganizationModel, table=True):
    title: str = Field()

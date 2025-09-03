import os
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from httpx import AsyncClient

from ..campaigns.models import ChannelType, CampaignGoal, Campaign as CampaignModel
from ..general.dataclasses import ResolvableCompanyModel
from ..integrations.dataclasses import LinkInfo


# Campaign object
class CampaignInfo(ResolvableCompanyModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    external_id: Optional[str]
    status: str
    last_sync_date: datetime
    ad_count: int
    channel: LinkInfo
    channel_type: ChannelType
    campaign_goal: Optional[CampaignGoal]

    @staticmethod
    async def resolve_object(object_id: UUID, organization_id: UUID) -> "CampaignInfo | None":
        result = await ResolveClient.campaigns().get(f"campaigns/{object_id}/resolve", headers={"X-Organization-ID": str(organization_id)})

        if result.status_code != 200:
            return None

        return CampaignInfo(**result.json())

    @classmethod
    async def from_model(cls: "CampaignInfo", model: CampaignModel) -> 'CampaignInfo':
        channel = await LinkInfo.resolve_object(model.channel_id, model.organization)

        return cls(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            organization=model.organization,
            name=model.name,
            external_id=model.external_id,
            status=model.status,
            last_sync_date=model.last_sync_date,
            ad_count=model.ad_count,
            channel=channel,
            channel_type=model.channel_type,
            campaign_goal=model.campaign_goal,
        )


class CampaignConfig(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

    name: str
    external_id: Optional[str]
    status: str
    last_sync_date: datetime
    ad_count: int
    channel_id: UUID
    channel_type: ChannelType
    campaign_goal: Optional[CampaignGoal]

    @classmethod
    async def from_model(cls: "CampaignConfig", model: CampaignModel) -> 'CampaignConfig':
        return cls(**model.model_dump())

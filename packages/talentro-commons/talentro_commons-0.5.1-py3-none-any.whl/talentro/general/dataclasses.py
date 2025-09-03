from abc import abstractmethod, ABC
from uuid import UUID

from pydantic import BaseModel

class ResolvableModel(BaseModel, ABC):

    @staticmethod
    @abstractmethod
    async def resolve_object(object_id: UUID) -> "ResolvableModel":
        pass


class ResolvableCompanyModel(BaseModel, ABC):

    @staticmethod
    @abstractmethod
    async def resolve_object(object_id: UUID, organization_id: str) -> "ResolvableCompanyModel":
        pass
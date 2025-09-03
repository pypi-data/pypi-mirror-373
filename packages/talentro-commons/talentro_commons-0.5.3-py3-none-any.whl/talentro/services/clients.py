import os

from httpx import AsyncClient

from talentro.util.singleton import SingletonMeta


class MSClient(metaclass=SingletonMeta):

    _integrations_client: AsyncClient | None = None
    _campaigns_client: AsyncClient | None = None
    _vacancies_client: AsyncClient | None = None

    @classmethod
    def integrations(cls) -> AsyncClient:
        if cls._integrations_client is None:
            cls._integrations_client = AsyncClient(
                base_url=f"{os.getenv('INTEGRATIONS_BASE_URL')}/api/v1/",
                timeout=30,
            )
        return cls._integrations_client

    @classmethod
    def campaigns(cls) -> AsyncClient:
        if cls._campaigns_client is None:
            cls._campaigns_client = AsyncClient(
                base_url=f"{os.getenv('CAMPAIGNS_BASE_URL')}/api/v1/",
                timeout=30,
            )
        return cls._campaigns_client

    @classmethod
    def vacancies(cls) -> AsyncClient:
        if cls._vacancies_client is None:
            cls._vacancies_client = AsyncClient(
                base_url=f"{os.getenv('VACANCIES_BASE_URL')}/api/v1/",
                timeout=30,
            )
        return cls._vacancies_client

    @classmethod
    async def aclose(cls) -> None:
        if cls._integrations_client is not None:
            await cls._integrations_client.aclose()
            cls._integrations_client = None
        if cls._campaigns_client is not None:
            await cls._campaigns_client.aclose()
            cls._campaigns_client = None
        if cls._vacancies_client is not None:
            await cls._vacancies_client.aclose()
            cls._vacancies_client = None

import json
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Queue(StrEnum):
    integrations = "integrations"
    candidates = "candidates"
    vacancies = "vacancies"
    strategy = "strategy"
    campaigns = "campaigns"
    insights = "insights"
    billing = "billing"
    iam = "iam"
    notifications = "notifications"
    live_updates = "live-updates"


@dataclass
class Event:
    event_type: str
    payload: dict
    organization_id: str | None = None
    created_on: datetime = None

    def encode(self) -> bytes:
        self.created_on: datetime = datetime.now()
        return json.dumps(self.__dict__, default=str).encode()


@dataclass
class Message:
    event: Event
    queue: Queue

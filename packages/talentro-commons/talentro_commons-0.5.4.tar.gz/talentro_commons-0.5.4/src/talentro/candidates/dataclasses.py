from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CandidateData(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    hashed_email: str
    cv: str
    motivation_letter: str
    linked_in: str


class Candidate(CandidateData):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID


class ApplicationData(BaseModel):
    status: str
    source: str
    candidate_id: str
    vacancy_id: str


class Application(ApplicationData):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    organization: UUID

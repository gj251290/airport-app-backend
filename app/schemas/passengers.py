from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PassengerCreate(BaseModel):
    reservation_id: UUID
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    document_number: str = Field(min_length=1)
    birth_date: date | None = None


class PassengerUpdate(BaseModel):
    reservation_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    document_number: str | None = None
    birth_date: date | None = None


class PassengerRead(BaseModel):
    id: UUID
    reservation_id: UUID
    first_name: str
    last_name: str
    document_number: str
    birth_date: date | None
    created_at: datetime

    class Config:
        from_attributes = True

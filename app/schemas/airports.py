from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AirportCreate(BaseModel):
    code: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    city: str | None = Field(default=None, min_length=1, max_length=100)


class AirportUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=10)
    name: str | None = Field(default=None, min_length=1)
    country: str | None = Field(default=None, min_length=1)
    city: str | None = Field(default=None, min_length=1, max_length=100)


class AirportRead(BaseModel):
    id: UUID
    code: str
    name: str
    country: str
    city: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AirlineCreate(BaseModel):
    code: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1)
    country: str | None = Field(default=None, min_length=1, max_length=100)


class AirlineUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=10)
    name: str | None = Field(default=None, min_length=1)
    country: str | None = Field(default=None, min_length=1, max_length=100)


class AirlineRead(BaseModel):
    id: UUID
    code: str
    name: str
    country: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

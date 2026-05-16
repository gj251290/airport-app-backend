from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

RESERVATION_STATUSES = {"HOLD", "CONFIRMED", "CANCELED", "EXPIRED"}


class ReservationCreate(BaseModel):
    user_id: UUID
    status: str | None = Field(default="HOLD")
    total_amount_cop: int | None = Field(default=0, ge=0)


class ReservationUpdate(BaseModel):
    user_id: UUID | None = None
    status: str | None = None
    total_amount_cop: int | None = Field(default=None, ge=0)


class ReservationRead(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_amount_cop: int
    created_at: datetime

    class Config:
        from_attributes = True

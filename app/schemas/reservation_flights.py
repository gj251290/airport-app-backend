from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReservationFlightCreate(BaseModel):
    reservation_id: UUID
    flight_id: UUID
    segment_order: int = Field(ge=1)


class ReservationFlightRead(BaseModel):
    id: UUID
    reservation_id: UUID
    flight_id: UUID
    segment_order: int
    created_at: datetime

    class Config:
        from_attributes = True

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

FLIGHT_STATUSES = {"SCHEDULED", "RESCHEDULED", "CANCELED"}


class FlightCreate(BaseModel):
    airline_id: UUID
    flight_number: str = Field(min_length=1)

    origin_airport_id: UUID
    destination_airport_id: UUID

    departure_at: datetime
    arrival_at: datetime

    status: str | None = Field(default="SCHEDULED")
    price_cop: int = 150000


class FlightUpdate(BaseModel):
    airline_id: UUID | None = None
    flight_number: str | None = None

    origin_airport_id: UUID | None = None
    destination_airport_id: UUID | None = None

    departure_at: datetime | None = None
    arrival_at: datetime | None = None

    status: str | None = None
    price_cop: int | None = None


class FlightRead(BaseModel):
    id: UUID
    airline_id: UUID
    flight_number: str
    origin_airport_id: UUID
    destination_airport_id: UUID
    departure_at: datetime
    arrival_at: datetime
    status: str
    price_cop: int
    created_at: datetime

    class Config:
        from_attributes = True

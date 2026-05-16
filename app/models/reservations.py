import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.passengers import Passenger
    from app.models.reservation_flights import ReservationFlight


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="HOLD")
    total_amount_cop: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="reservations")
    passengers: Mapped[List["Passenger"]] = relationship(
        back_populates="reservation", cascade="all, delete-orphan"
    )
    flights: Mapped[List["ReservationFlight"]] = relationship(
        back_populates="reservation", cascade="all, delete-orphan"
    )

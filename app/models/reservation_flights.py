import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, func, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.reservations import Reservation
    from app.models.flights import Flight


class ReservationFlight(Base):
    __tablename__ = "reservation_flights"
    __table_args__ = (
        UniqueConstraint("reservation_id", "flight_id", name="uq_reservation_flight"),
        UniqueConstraint(
            "reservation_id", "segment_order", name="uq_reservation_segment"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    reservation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reservations.id"),
        nullable=False,
    )

    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flights.id"),
        nullable=False,
    )

    segment_order: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    reservation: Mapped["Reservation"] = relationship(back_populates="flights")
    flight: Mapped["Flight"] = relationship()

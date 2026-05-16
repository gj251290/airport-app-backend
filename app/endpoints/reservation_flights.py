from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database.session import get_db
from app.models.flights import Flight
from app.models.reservations import Reservation
from app.models.reservation_flights import ReservationFlight
from app.schemas.reservation_flights import (
    ReservationFlightCreate,
    ReservationFlightRead,
)
from app.services.pricing import recalculate_reservation_total

from app.core.exceptions import NotFoundError, ConflictError, ValidationError

router = APIRouter(prefix="/api/reservation-flights", tags=["reservation-flights"])


@router.get("", response_model=list[ReservationFlightRead])
async def list_reservation_flights(
    reservation_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[ReservationFlight]:
    stmt = select(ReservationFlight).order_by(ReservationFlight.created_at.desc())

    if reservation_id is not None:
        stmt = (
            select(ReservationFlight)
            .where(ReservationFlight.reservation_id == reservation_id)
            .order_by(ReservationFlight.segment_order.asc())
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "", response_model=ReservationFlightRead, status_code=status.HTTP_201_CREATED
)
async def create_reservation_flight(
    payload: ReservationFlightCreate,
    db: AsyncSession = Depends(get_db),
) -> ReservationFlight:
    reservation = await db.get(Reservation, payload.reservation_id)
    if not reservation:
        raise ValidationError("Invalid reservation_id")

    # (Recomendado) bloquear cambios si ya está confirmada
    if reservation.status == "CONFIRMED":
        raise ConflictError("Reservation is CONFIRMED; flights cannot be modified")

    if not await db.get(Flight, payload.flight_id):
        raise ValidationError("Invalid flight_id")

    rf = ReservationFlight(
        reservation_id=payload.reservation_id,
        flight_id=payload.flight_id,
        segment_order=payload.segment_order,
    )
    db.add(rf)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictError("Duplicate flight or segment_order for this reservation")

    await db.refresh(rf)

    # NEW: recalcular y persistir total
    await recalculate_reservation_total(db, payload.reservation_id)
    await db.commit()

    return rf


@router.delete("/{reservation_flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation_flight(
    reservation_flight_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    rf = await db.get(ReservationFlight, reservation_flight_id)
    if not rf:
        raise NotFoundError("Reservation flight not found")

    reservation = await db.get(Reservation, rf.reservation_id)
    if reservation and reservation.status == "CONFIRMED":
        raise ConflictError("Reservation is CONFIRMED; flights cannot be modified")

    reservation_id = rf.reservation_id

    await db.delete(rf)
    await db.commit()

    # NEW: recalcular y persistir total
    await recalculate_reservation_total(db, reservation_id)
    await db.commit()

    return None

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.passengers import Passenger
from app.models.reservations import Reservation
from app.schemas.passengers import PassengerCreate, PassengerRead, PassengerUpdate
from app.services.pricing import recalculate_reservation_total

from app.core.exceptions import NotFoundError, ConflictError, ValidationError

router = APIRouter(prefix="/api/passengers", tags=["passengers"])


@router.get("", response_model=list[PassengerRead])
async def list_passengers(
    reservation_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[Passenger]:
    stmt = select(Passenger).order_by(Passenger.created_at.desc())
    if reservation_id is not None:
        stmt = (
            select(Passenger)
            .where(Passenger.reservation_id == reservation_id)
            .order_by(Passenger.created_at.desc())
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{passenger_id}", response_model=PassengerRead)
async def get_passenger(
    passenger_id: UUID, db: AsyncSession = Depends(get_db)
) -> Passenger:
    passenger = await db.get(Passenger, passenger_id)
    if not passenger:
        raise NotFoundError("Passenger not found")
    return passenger


@router.post("", response_model=PassengerRead, status_code=status.HTTP_201_CREATED)
async def create_passenger(
    payload: PassengerCreate, db: AsyncSession = Depends(get_db)
) -> Passenger:
    reservation = await db.get(Reservation, payload.reservation_id)
    if not reservation:
        raise ValidationError("Invalid reservation_id")

    # (Recomendado) bloquear cambios si ya está confirmada
    if reservation.status == "CONFIRMED":
        raise ConflictError("Reservation is CONFIRMED; passengers cannot be added")

    passenger = Passenger(
        reservation_id=payload.reservation_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        document_number=payload.document_number,
        birth_date=payload.birth_date,
    )
    db.add(passenger)
    await db.commit()
    await db.refresh(passenger)

    # NEW: recalcular y persistir total
    await recalculate_reservation_total(db, payload.reservation_id)
    await db.commit()

    return passenger


@router.put("/{passenger_id}", response_model=PassengerRead)
async def update_passenger(
    passenger_id: UUID, payload: PassengerUpdate, db: AsyncSession = Depends(get_db)
) -> Passenger:
    passenger = await db.get(Passenger, passenger_id)
    if not passenger:
        raise NotFoundError("Passenger not found")

    # (Recomendado) bloquear cambios si la reserva está confirmada
    current_reservation = await db.get(Reservation, passenger.reservation_id)
    if current_reservation and current_reservation.status == "CONFIRMED":
        raise ConflictError("Reservation is CONFIRMED; passengers cannot be added")

    old_reservation_id = passenger.reservation_id

    if payload.reservation_id is not None:
        reservation = await db.get(Reservation, payload.reservation_id)
        if not reservation:
            raise ValidationError("Invalid reservation_id")
        if reservation.status == "CONFIRMED":
            raise ConflictError("Reservation is CONFIRMED; passengers cannot be added")
        passenger.reservation_id = payload.reservation_id

    if payload.first_name is not None:
        passenger.first_name = payload.first_name
    if payload.last_name is not None:
        passenger.last_name = payload.last_name
    if payload.document_number is not None:
        passenger.document_number = payload.document_number
    if payload.birth_date is not None:
        passenger.birth_date = payload.birth_date

    await db.commit()
    await db.refresh(passenger)

    # NEW: recalcular si cambió reservation_id (o por consistencia)
    if passenger.reservation_id != old_reservation_id:
        await recalculate_reservation_total(db, old_reservation_id)
    await recalculate_reservation_total(db, passenger.reservation_id)
    await db.commit()

    return passenger


@router.delete("/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_passenger(
    passenger_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    passenger = await db.get(Passenger, passenger_id)
    if not passenger:
        raise NotFoundError("Passenger not found")

    reservation = await db.get(Reservation, passenger.reservation_id)
    if reservation and reservation.status == "CONFIRMED":
        raise ConflictError("Reservation is CONFIRMED; passengers cannot be added")

    reservation_id = passenger.reservation_id

    await db.delete(passenger)
    await db.commit()

    # NEW: recalcular y persistir total
    await recalculate_reservation_total(db, reservation_id)
    await db.commit()

    return None

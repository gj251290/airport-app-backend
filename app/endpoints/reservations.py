from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.reservations import Reservation
from app.models.user import User
from app.schemas.reservations import (
    RESERVATION_STATUSES,
    ReservationCreate,
    ReservationRead,
    ReservationUpdate,
)

from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationRead])
async def list_reservations(db: AsyncSession = Depends(get_db)) -> list[Reservation]:
    result = await db.execute(
        select(Reservation).order_by(Reservation.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{reservation_id}", response_model=ReservationRead)
async def get_reservation(
    reservation_id: UUID, db: AsyncSession = Depends(get_db)
) -> Reservation:
    reservation = await db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError("Reservation not found")
    return reservation


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    payload: ReservationCreate, db: AsyncSession = Depends(get_db)
) -> Reservation:
    user = await db.get(User, payload.user_id)
    if not user:
        raise ValidationError("Invalid user_id")

    status_value = payload.status or "HOLD"
    if status_value not in RESERVATION_STATUSES:
        raise ValidationError(
            f"Invalid status. Must be one of: {sorted(RESERVATION_STATUSES)}"
        )

    reservation = Reservation(
        user_id=payload.user_id,
        status=status_value,
        total_amount_cop=payload.total_amount_cop or 0,
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.put("/{reservation_id}", response_model=ReservationRead)
async def update_reservation(
    reservation_id: UUID, payload: ReservationUpdate, db: AsyncSession = Depends(get_db)
) -> Reservation:
    reservation = await db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError("Reservation not found")

    if payload.user_id is not None:
        user = await db.get(User, payload.user_id)
        if not user:
            raise ValidationError("Invalid user_id")
        reservation.user_id = payload.user_id

    if payload.status is not None:
        if payload.status not in RESERVATION_STATUSES:
            raise ValidationError(
                f"Invalid status. Must be one of: {sorted(RESERVATION_STATUSES)}"
            )
        reservation.status = payload.status

    if payload.total_amount_cop is not None:
        reservation.total_amount_cop = payload.total_amount_cop

    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    reservation = await db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError("Reservation not found")

    await db.delete(reservation)
    await db.commit()
    return None

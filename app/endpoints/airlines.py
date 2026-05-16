from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.airlines import Airline
from app.schemas.airlines import AirlineCreate, AirlineRead, AirlineUpdate

from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/api/airlines", tags=["airlines"])


@router.get("", response_model=list[AirlineRead])
async def list_airlines(db: AsyncSession = Depends(get_db)) -> list[Airline]:
    result = await db.execute(select(Airline).order_by(Airline.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{airline_id}", response_model=AirlineRead)
async def get_airline(airline_id: UUID, db: AsyncSession = Depends(get_db)) -> Airline:
    airline = await db.get(Airline, airline_id)
    if not airline:
        raise NotFoundError("Aerolinea no encontrada")
    return airline


@router.post("", response_model=AirlineRead, status_code=status.HTTP_201_CREATED)
async def create_airline(
    payload: AirlineCreate, db: AsyncSession = Depends(get_db)
) -> Airline:
    existing = await db.execute(select(Airline).where(Airline.code == payload.code))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("Esta Aerolinea ya existe")

    # NEW: country
    airline = Airline(code=payload.code, name=payload.name, country=payload.country)
    db.add(airline)
    await db.commit()
    await db.refresh(airline)
    return airline


@router.put("/{airline_id}", response_model=AirlineRead)
async def update_airline(
    airline_id: UUID, payload: AirlineUpdate, db: AsyncSession = Depends(get_db)
) -> Airline:
    airline = await db.get(Airline, airline_id)
    if not airline:
        raise NotFoundError("Aerolinea no encontrada")

    if payload.code is not None:
        existing = await db.execute(
            select(Airline).where(
                Airline.code == payload.code, Airline.id != airline_id
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError("Esta Aerolinea ya existe")
        airline.code = payload.code

    if payload.name is not None:
        airline.name = payload.name

    # NEW: country (se puede setear a None)
    if payload.country is not None:
        airline.country = payload.country

    await db.commit()
    await db.refresh(airline)
    return airline


@router.delete("/{airline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_airline(airline_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    airline = await db.get(Airline, airline_id)
    if not airline:
        raise NotFoundError("Aerolinea no encontrada")

    await db.delete(airline)
    await db.commit()
    return None

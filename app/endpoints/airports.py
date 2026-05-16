from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.airports import Airport
from app.schemas.airports import AirportCreate, AirportRead, AirportUpdate

from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/api/airports", tags=["airports"])


@router.get("", response_model=list[AirportRead])
async def list_airports(db: AsyncSession = Depends(get_db)) -> list[Airport]:
    result = await db.execute(select(Airport).order_by(Airport.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{airport_id}", response_model=AirportRead)
async def get_airport(airport_id: UUID, db: AsyncSession = Depends(get_db)) -> Airport:
    airport = await db.get(Airport, airport_id)
    if not airport:
        raise NotFoundError("Airport not found")
    return airport


@router.post("", response_model=AirportRead, status_code=status.HTTP_201_CREATED)
async def create_airport(
    payload: AirportCreate, db: AsyncSession = Depends(get_db)
) -> Airport:
    existing = await db.execute(select(Airport).where(Airport.code == payload.code))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("Airport code already exists")

    # NEW: city
    airport = Airport(
        code=payload.code,
        name=payload.name,
        country=payload.country,
        city=payload.city,
    )
    db.add(airport)
    await db.commit()
    await db.refresh(airport)
    return airport


@router.put("/{airport_id}", response_model=AirportRead)
async def update_airport(
    airport_id: UUID, payload: AirportUpdate, db: AsyncSession = Depends(get_db)
) -> Airport:
    airport = await db.get(Airport, airport_id)
    if not airport:
        raise NotFoundError("Airport not found")

    if payload.code is not None:
        existing = await db.execute(
            select(Airport).where(
                Airport.code == payload.code, Airport.id != airport_id
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError("Airport code already exists")
        airport.code = payload.code

    if payload.name is not None:
        airport.name = payload.name

    if payload.country is not None:
        airport.country = payload.country

    if payload.city is not None:
        airport.city = payload.city

    await db.commit()
    await db.refresh(airport)
    return airport


@router.delete("/{airport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_airport(airport_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    airport = await db.get(Airport, airport_id)
    if not airport:
        raise NotFoundError("Airport not found")

    await db.delete(airport)
    await db.commit()
    return None

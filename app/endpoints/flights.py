from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.airlines import Airline
from app.models.airports import Airport
from app.models.flights import Flight
from app.schemas.flights import FLIGHT_STATUSES, FlightCreate, FlightRead, FlightUpdate

from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/flights", tags=["flights"])


def _validate_flight_rules(
    origin_airport_id: UUID,
    destination_airport_id: UUID,
    departure_at,
    arrival_at,
    status_value: str,
) -> None:
    if origin_airport_id == destination_airport_id:
        raise ValidationError(
            "origin_airport_id must be different from destination_airport_id"
        )

    if arrival_at <= departure_at:
        raise ValidationError("arrival_at must be greater than departure_at")

    if status_value not in FLIGHT_STATUSES:
        raise ValidationError(
            f"Invalid status. Must be one of: {sorted(FLIGHT_STATUSES)}"
        )


@router.get("", response_model=list[FlightRead])
async def list_flights(db: AsyncSession = Depends(get_db)) -> list[Flight]:
    result = await db.execute(select(Flight).order_by(Flight.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{flight_id}", response_model=FlightRead)
async def get_flight(flight_id: UUID, db: AsyncSession = Depends(get_db)) -> Flight:
    flight = await db.get(Flight, flight_id)
    if not flight:
        raise NotFoundError("Flights not found")
    return flight


@router.post("", response_model=FlightRead, status_code=status.HTTP_201_CREATED)
async def create_flight(
    payload: FlightCreate, db: AsyncSession = Depends(get_db)
) -> Flight:
    status_value = payload.status or "SCHEDULED"
    _validate_flight_rules(
        origin_airport_id=payload.origin_airport_id,
        destination_airport_id=payload.destination_airport_id,
        departure_at=payload.departure_at,
        arrival_at=payload.arrival_at,
        status_value=status_value,
    )

    airline = await db.get(Airline, payload.airline_id)
    if not airline:
        raise ValidationError("Invalid airline_id")
    origin = await db.get(Airport, payload.origin_airport_id)
    if not origin:
        raise ValidationError("Invalid origin_airport_id")
    dest = await db.get(Airport, payload.destination_airport_id)
    if not dest:
        raise ValidationError("Invalid destination_airport_id")
    # FIX: asignar price_cop (siempre) para que nunca sea None en la respuesta
    flight = Flight(
        airline_id=payload.airline_id,
        flight_number=payload.flight_number,
        origin_airport_id=payload.origin_airport_id,
        destination_airport_id=payload.destination_airport_id,
        departure_at=payload.departure_at,
        arrival_at=payload.arrival_at,
        status=status_value,
        price_cop=payload.price_cop,
    )
    db.add(flight)
    await db.commit()
    await db.refresh(flight)
    return flight


@router.put("/{flight_id}", response_model=FlightRead)
async def update_flight(
    flight_id: UUID, payload: FlightUpdate, db: AsyncSession = Depends(get_db)
) -> Flight:
    flight = await db.get(Flight, flight_id)
    if not flight:
        raise NotFoundError("Flights not found")

    # Proponer valores finales (para validar reglas de negocio)
    """ airline_id = (
        payload.airline_id if payload.airline_id is not None else flight.airline_id
    ) """
    origin_airport_id = (
        payload.origin_airport_id
        if payload.origin_airport_id is not None
        else flight.origin_airport_id
    )
    destination_airport_id = (
        payload.destination_airport_id
        if payload.destination_airport_id is not None
        else flight.destination_airport_id
    )
    departure_at = (
        payload.departure_at
        if payload.departure_at is not None
        else flight.departure_at
    )
    arrival_at = (
        payload.arrival_at if payload.arrival_at is not None else flight.arrival_at
    )
    status_value = payload.status if payload.status is not None else flight.status

    _validate_flight_rules(
        origin_airport_id=origin_airport_id,
        destination_airport_id=destination_airport_id,
        departure_at=departure_at,
        arrival_at=arrival_at,
        status_value=status_value,
    )

    # Validar FKs solo si cambian (o si payload lo trae)
    if payload.airline_id is not None:
        if not await db.get(Airline, payload.airline_id):
            raise ValidationError("Invalid airline_id")
        flight.airline_id = payload.airline_id

    if payload.origin_airport_id is not None:
        if not await db.get(Airport, payload.origin_airport_id):
            raise ValidationError("Invalid origin_airport_id")
        flight.origin_airport_id = payload.origin_airport_id

    if payload.destination_airport_id is not None:
        if not await db.get(Airport, payload.destination_airport_id):
            raise ValidationError("Invalid destination_airport_id")
        flight.destination_airport_id = payload.destination_airport_id

    if payload.flight_number is not None:
        flight.flight_number = payload.flight_number

    if payload.departure_at is not None:
        flight.departure_at = payload.departure_at

    if payload.arrival_at is not None:
        flight.arrival_at = payload.arrival_at

    if payload.status is not None:
        flight.status = payload.status

    # FIX: permitir actualizar price_cop (y evitar que quede None)
    if payload.price_cop is not None:
        flight.price_cop = payload.price_cop

    await db.commit()
    await db.refresh(flight)
    return flight


@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(flight_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    flight = await db.get(Flight, flight_id)
    if not flight:
        raise NotFoundError("Flights not found")

    await db.delete(flight)
    await db.commit()
    return None

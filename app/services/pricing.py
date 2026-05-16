from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flights import Flight
from app.models.passengers import Passenger
from app.models.reservations import Reservation
from app.models.reservation_flights import ReservationFlight


async def recalculate_reservation_total(db: AsyncSession, reservation_id: UUID) -> int:
    """
    Recalcula reservations.total_amount_cop para una reserva.

    Regla MVP:
      total_amount_cop = sum(price_cop de vuelos asociados) * cantidad_pasajeros

    Nota:
      - Esta función NO hace commit. El endpoint debe hacer commit.
      - Esta función sí hace flush para que el cambio quede aplicado en la transacción actual.
    """
    flights_sum_stmt = (
        select(func.coalesce(func.sum(Flight.price_cop), 0))
        .select_from(ReservationFlight)
        .join(Flight, Flight.id == ReservationFlight.flight_id)
        .where(ReservationFlight.reservation_id == reservation_id)
    )
    flights_sum = (await db.execute(flights_sum_stmt)).scalar_one()

    pax_count_stmt = select(func.count(Passenger.id)).where(
        Passenger.reservation_id == reservation_id
    )
    pax_count = (await db.execute(pax_count_stmt)).scalar_one()

    total = int(flights_sum) * int(pax_count)

    reservation = await db.get(Reservation, reservation_id)
    if not reservation:
        return total

    reservation.total_amount_cop = total
    await db.flush()

    return total

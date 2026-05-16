from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def list_reservation_flights_by_reservation(
    client: APIClient, reservation_id: str
) -> list[dict[str, Any]]:
    r = client.get(
        "/api/reservation-flights", params={"reservation_id": reservation_id}
    )
    r.raise_for_status()
    return r.json()


def create_reservation_flight(
    client: APIClient,
    *,
    reservation_id: str,
    flight_id: str,
    segment_order: int,
) -> dict[str, Any]:
    payload = {
        "reservation_id": reservation_id,
        "flight_id": flight_id,
        "segment_order": segment_order,
    }
    r = client.post("/api/reservation-flights", json=payload)
    r.raise_for_status()
    return r.json()


def delete_reservation_flight(client: APIClient, reservation_flight_id: str) -> None:
    r = client.delete(f"/api/reservation-flights/{reservation_flight_id}")
    r.raise_for_status()

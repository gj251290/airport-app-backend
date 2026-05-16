from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def list_passengers_by_reservation(
    client: APIClient, reservation_id: str
) -> list[dict[str, Any]]:

    r = client.get("/api/passengers", params={"reservation_id": reservation_id})
    r.raise_for_status()
    return r.json()


def create_passenger(
    client: APIClient,
    *,
    reservation_id: str,
    first_name: str,
    last_name: str,
    document_number: str,
    birth_date: str | None = None,
) -> dict[str, Any]:

    payload: dict[str, Any] = {
        "reservation_id": reservation_id,
        "first_name": first_name,
        "last_name": last_name,
        "document_number": document_number,
    }
    if birth_date:
        payload["birth_date"] = birth_date

    r = client.post("/api/passengers", json=payload)
    r.raise_for_status()
    return r.json()


def delete_passenger(client: APIClient, passenger_id: str) -> None:

    r = client.delete(f"/api/passengers/{passenger_id}")
    r.raise_for_status()

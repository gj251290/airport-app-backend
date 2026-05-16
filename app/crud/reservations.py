from typing import Any

from app.crud.http_client import APIClient


def list_reservations(client: APIClient) -> list[dict[str, Any]]:
    r = client.get("/api/reservations")
    r.raise_for_status()
    return r.json()


def get_reservation(client: APIClient, reservation_id: str) -> dict[str, Any]:
    r = client.get(f"/api/reservations/{reservation_id}")
    r.raise_for_status()
    return r.json()


def create_reservation(client: APIClient, payload: dict[str, Any]) -> dict[str, Any]:
    r = client.post("/api/reservations", json=payload)
    r.raise_for_status()
    return r.json()


def update_reservation(
    client: APIClient, reservation_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    r = client.put(f"/api/reservations/{reservation_id}", json=payload)
    r.raise_for_status()
    return r.json()


def delete_reservation(client: APIClient, reservation_id: str) -> None:
    r = client.delete(f"/api/reservations/{reservation_id}")
    r.raise_for_status()

from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def list_flights(client: APIClient) -> list[dict[str, Any]]:
    r = client.get("/api/flights")
    r.raise_for_status()
    return r.json()


def get_flight(client: APIClient, flight_id: str) -> dict[str, Any]:
    r = client.get(f"/api/flights/{flight_id}")
    r.raise_for_status()
    return r.json()


def create_flight(client: APIClient, payload: dict[str, Any]) -> dict[str, Any]:
    r = client.post("/api/flights", json=payload)
    r.raise_for_status()
    return r.json()


def update_flight(
    client: APIClient, flight_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    r = client.put(f"/api/flights/{flight_id}", json=payload)
    r.raise_for_status()
    return r.json()


def delete_flight(client: APIClient, flight_id: str) -> None:
    r = client.delete(f"/api/flights/{flight_id}")
    r.raise_for_status()

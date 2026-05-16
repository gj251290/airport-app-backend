from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def list_airports(client: APIClient) -> list[dict[str, Any]]:
    r = client.get("/api/airports")
    r.raise_for_status()
    return r.json()


def get_airport(client: APIClient, airport_id: str) -> dict[str, Any]:
    r = client.get(f"/api/airports/{airport_id}")
    r.raise_for_status()
    return r.json()


def create_airport(client: APIClient, payload: dict[str, Any]) -> dict[str, Any]:
    r = client.post("/api/airports", json=payload)
    r.raise_for_status()
    return r.json()


def update_airport(
    client: APIClient, airport_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    r = client.put(f"/api/airports/{airport_id}", json=payload)
    r.raise_for_status()
    return r.json()


def delete_airport(client: APIClient, airport_id: str) -> None:
    r = client.delete(f"/api/airports/{airport_id}")
    r.raise_for_status()

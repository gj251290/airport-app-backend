from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def list_airlines(client: APIClient) -> list[dict[str, Any]]:
    r = client.get("/api/airlines")
    r.raise_for_status()
    return r.json()


def get_airline(client: APIClient, airline_id: str) -> dict[str, Any]:
    r = client.get(f"/api/airlines/{airline_id}")
    r.raise_for_status()
    return r.json()


def create_airline(client: APIClient, payload: dict[str, Any]) -> dict[str, Any]:
    r = client.post("/api/airlines", json=payload)
    r.raise_for_status()
    return r.json()


def update_airline(
    client: APIClient, airline_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    r = client.put(f"/api/airlines/{airline_id}", json=payload)
    r.raise_for_status()
    return r.json()


def delete_airline(client: APIClient, airline_id: str) -> None:
    r = client.delete(f"/api/airlines/{airline_id}")
    r.raise_for_status()

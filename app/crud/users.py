from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def list_users(client: APIClient) -> list[dict[str, Any]]:
    r = client.get("/api/users")
    r.raise_for_status()
    return r.json()


def get_user(client: APIClient, user_id: str) -> dict[str, Any]:
    r = client.get(f"/api/users/{user_id}")
    r.raise_for_status()
    return r.json()


def create_user(client: APIClient, payload: dict[str, Any]) -> dict[str, Any]:
    r = client.post("/api/users", json=payload)
    r.raise_for_status()
    return r.json()


def update_user(
    client: APIClient, user_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    r = client.put(f"/api/users/{user_id}", json=payload)
    r.raise_for_status()
    return r.json()


def delete_user(client: APIClient, user_id: str) -> None:
    r = client.delete(f"/api/users/{user_id}")
    r.raise_for_status()

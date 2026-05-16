from __future__ import annotations

from typing import Any

from app.crud.http_client import APIClient


def login(client: APIClient, *, email: str, password: str) -> dict[str, Any]:
    data = {"username": email, "password": password}
    response = client.client.post("/api/auth/login", data=data)
    response.raise_for_status()
    return response.json()

from __future__ import annotations

from typing import Any

import httpx


class APIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=15)

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        return self.client.get(path, params=params)

    def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self.client.post(path, json=json, params=params)

    def put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self.client.put(path, json=json, params=params)

    def delete(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        return self.client.delete(path, params=params)

    def close(self) -> None:
        self.client.close()

    def set_bearer_token(self, token: str) -> None:
        if token:
            self.client.headers.update({"Authorization": f"Bearer {token}"})

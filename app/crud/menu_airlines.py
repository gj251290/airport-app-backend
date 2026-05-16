from __future__ import annotations

from typing import Any

import httpx
from rich.console import Console

from app.crud.airlines import (
    create_airline,
    delete_airline,
    get_airline,
    list_airlines,
    update_airline,
)
from app.crud.http_client import APIClient
from app.utils.cli_utils import clear_screen, pause, print_table

console = Console()


def _handle_http_error(exc: Exception) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail")
        except Exception:
            detail = exc.response.text
        console.print(f"\n[red]HTTP {exc.response.status_code}[/red]: {detail}\n")
    else:
        console.print(f"\n[red]Error[/red]: {exc}\n")


def airlines_menu(client: APIClient) -> None:
    payload: dict[str, Any]

    while True:
        clear_screen()
        console.print("=== AEROLÍNEAS ===\n")
        console.print("1) Listar aerolíneas")
        console.print("2) Ver aerolínea")
        console.print("3) Crear aerolínea")
        console.print("4) Actualizar aerolínea")
        console.print("5) Eliminar aerolínea")
        console.print("0) Volver")
        console.print("----------------------")

        op = input("Opción: ").strip()

        try:
            if op == "0":
                return

            if op == "1":
                rows = list_airlines(client)
                print_table(
                    rows,
                    columns={
                        "code": "Código",
                        "name": "Nombre",
                        "country": "País",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Aerolíneas",
                    empty_message="No hay aerolíneas.",
                )
                pause()

            elif op == "2":
                rows = list_airlines(client)
                if not rows:
                    console.print("No hay aerolíneas.")
                    pause()
                    continue

                console.print("\nSelecciona por número:\n")
                for idx, a in enumerate(rows, start=1):
                    console.print(f"{idx}) {a.get('code')} | {a.get('name')}")

                console.print("0) Cancelar")
                raw = input("Opción: ").strip()
                if raw == "0":
                    continue
                if not raw.isdigit() or not (1 <= int(raw) <= len(rows)):
                    console.print("Opción inválida.")
                    pause()
                    continue

                airline_id = rows[int(raw) - 1]["id"]
                a = get_airline(client, airline_id)
                print_table(
                    [a],
                    columns={
                        "code": "Código",
                        "name": "Nombre",
                        "country": "País",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Aerolínea",
                )
                pause()

            elif op == "3":
                clear_screen()
                console.print("=== Crear aerolínea ===\n")
                code = input("Código (ej: AVA, LAT, AAL): ").strip()
                name = input("Nombre (ej: Avianca): ").strip()
                country = input("País (opcional): ").strip()

                payload = {"code": code, "name": name}
                if country:
                    payload["country"] = country

                created = create_airline(client, payload)
                console.print(
                    f"\nAerolínea creada: {created['code']} ({created['id']})\n"
                )
                pause()

            elif op == "4":
                rows = list_airlines(client)
                if not rows:
                    console.print("No hay aerolíneas.")
                    pause()
                    continue

                console.print("\nSelecciona por número:\n")
                for idx, a in enumerate(rows, start=1):
                    console.print(f"{idx}) {a.get('code')} | {a.get('name')}")

                console.print("0) Cancelar")
                raw = input("Opción: ").strip()
                if raw == "0":
                    continue
                if not raw.isdigit() or not (1 <= int(raw) <= len(rows)):
                    console.print("Opción inválida.")
                    pause()
                    continue

                picked = rows[int(raw) - 1]
                airline_id = picked["id"]

                clear_screen()
                console.print("=== Actualizar aerolínea ===\n")
                console.print("deja en blanco para mantener el valor actual\n")
                console.print(f"Actual: {picked.get('code')} | {picked.get('name')}\n")

                current_code = picked.get("code") or ""
                current_name = picked.get("name") or ""

                code = (
                    input(f"Código [{current_code}]: ").strip().upper() or current_code
                )
                name = input(f"Nombre [{current_name}]: ").strip() or current_name
                country = input(f"País [{picked.get('country','')}]: ").strip()

                payload = {"code": code, "name": name}
                if country != "":
                    payload["country"] = country

                updated = update_airline(client, airline_id, payload)
                console.print(
                    f"\nAerolínea actualizada: {updated['code']} ({updated['id']})\n"
                )
                pause()

            elif op == "5":
                rows = list_airlines(client)
                if not rows:
                    console.print("No hay aerolíneas.")
                    pause()
                    continue

                console.print("\nSelecciona por número:\n")
                for idx, a in enumerate(rows, start=1):
                    console.print(f"{idx}) {a.get('code')} | {a.get('name')}")

                console.print("0) Cancelar")
                raw = input("Opción: ").strip()
                if raw == "0":
                    continue
                if not raw.isdigit() or not (1 <= int(raw) <= len(rows)):
                    console.print("Opción inválida.")
                    pause()
                    continue

                picked = rows[int(raw) - 1]
                confirm = (
                    input(
                        f"¿Eliminar {picked.get('code')} {picked.get('name')}? (s/N): "
                    )
                    .strip()
                    .lower()
                )
                if confirm != "s":
                    continue

                delete_airline(client, picked["id"])
                console.print("\nAerolínea eliminada.\n")
                pause()

            else:
                console.print("Opción inválida.")
                pause()

        except Exception as exc:
            _handle_http_error(exc)
            pause()

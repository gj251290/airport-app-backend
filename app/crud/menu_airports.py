from __future__ import annotations

from typing import Any

import httpx
from rich.console import Console

from app.crud.airports import (
    create_airport,
    delete_airport,
    get_airport,
    list_airports,
    update_airport,
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


def airports_menu(client: APIClient) -> None:
    payload: dict[str, Any]

    while True:
        clear_screen()
        console.print("=== AEROPUERTOS ===\n")
        console.print("1) Listar aeropuertos")
        console.print("2) Ver aeropuerto")
        console.print("3) Crear aeropuerto")
        console.print("4) Actualizar aeropuerto")
        console.print("5) Eliminar aeropuerto")
        console.print("0) Volver")
        console.print("----------------------")

        op = input("Opción: ").strip()

        try:
            if op == "0":
                return

            if op == "1":
                rows = list_airports(client)
                print_table(
                    rows,
                    columns={
                        "code": "Código",
                        "name": "Nombre",
                        "city": "Ciudad",
                        "country": "País",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Aeropuertos",
                    empty_message="No hay aeropuertos.",
                )
                pause()

            elif op == "2":
                rows = list_airports(client)
                if not rows:
                    console.print("No hay aeropuertos.")
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

                airport_id = rows[int(raw) - 1]["id"]
                a = get_airport(client, airport_id)
                print_table(
                    [a],
                    columns={
                        "code": "Código",
                        "name": "Nombre",
                        "city": "Ciudad",
                        "country": "País",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Aeropuerto",
                )
                pause()

            elif op == "3":
                clear_screen()
                console.print("=== Crear aeropuerto ===\n")
                code = input("Código IATA (ej: BOG, MDE, JFK): ").strip().upper()
                name = input("Nombre: ").strip()
                city = input("Ciudad (opcional): ").strip()
                country = input("País (opcional): ").strip()

                payload = {"code": code, "name": name}
                if city:
                    payload["city"] = city
                if country:
                    payload["country"] = country

                created = create_airport(client, payload)
                console.print(
                    f"\nAeropuerto creado: {created['code']} ({created['id']})\n"
                )
                pause()

            elif op == "4":
                rows = list_airports(client)
                if not rows:
                    console.print("No hay aeropuertos.")
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
                airport_id = picked["id"]

                clear_screen()
                console.print("=== Actualizar aeropuerto ===\n")
                console.print(f"Actual: {picked.get('code')} | {picked.get('name')}\n")

                current_code = picked.get("code") or ""
                current_name = picked.get("name") or ""

                code = (
                    input(f"Código [{current_code}]: ").strip().upper() or current_code
                )
                name = input(f"Nombre [{current_name}]: ").strip() or current_name

                city = input(f"Ciudad [{picked.get('city','')}]: ").strip()
                country = input(f"País [{picked.get('country','')}]: ").strip()

                payload = {"code": code, "name": name}
                if city != "":
                    payload["city"] = city
                if country != "":
                    payload["country"] = country

                updated = update_airport(client, airport_id, payload)
                console.print(
                    f"\nAeropuerto actualizado: {updated['code']} ({updated['id']})\n"
                )
                pause()

            elif op == "5":
                rows = list_airports(client)
                if not rows:
                    console.print("No hay aeropuertos.")
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

                delete_airport(client, picked["id"])
                console.print("\nAeropuerto eliminado.\n")
                pause()

            else:
                console.print("Opción inválida.")
                pause()

        except Exception as exc:
            _handle_http_error(exc)
            pause()

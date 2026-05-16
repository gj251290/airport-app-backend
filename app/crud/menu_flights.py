from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

import httpx
from rich.console import Console

from app.crud.airlines import list_airlines
from app.crud.airports import list_airports
from app.crud.flights import (
    create_flight,
    delete_flight,
    get_flight,
    list_flights,
    update_flight,
)
from app.crud.http_client import APIClient
from app.utils.cli_utils import clear_screen, pause, print_table

console = Console()


FLIGHT_STATUSES = ["SCHEDULED", "RESCHEDULED", "CANCELED"]


def _handle_http_error(exc: Exception) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail")
        except Exception:
            detail = exc.response.text
        console.print(f"\n[red]HTTP {exc.response.status_code}[/red]: {detail}\n")
    else:
        console.print(f"\n[red]Error[/red]: {exc}\n")


def _parse_dt(value: str) -> str:
    try:
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return value


def _parse_cli_datetime_to_iso(value: str) -> str:
    """
    Accepts:
      - 'YYYY-MM-DD HH:MM' (assumes UTC)
      - ISO strings (passes through)
    Returns ISO string with timezone (UTC).
    """
    raw = value.strip()
    if not raw:
        raise ValueError("Fecha/hora vacía")

    try:
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        pass

    v = raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _build_id_map(
    rows: list[dict[str, Any]], id_key: str = "id"
) -> dict[str, dict[str, Any]]:
    return {str(r[id_key]): r for r in rows}


def _pick_from_list(
    items: list[dict[str, Any]],
    *,
    item_label: Callable[[dict[str, Any]], str],
    title: str,
) -> dict[str, Any] | None:
    if not items:
        console.print("No hay datos para seleccionar.")
        return None

    console.print(f"{title}\n")
    for idx, it in enumerate(items, start=1):
        console.print(f"{idx}) {item_label(it)}")
    console.print("0) Cancelar")

    while True:
        raw = input("Opción: ").strip()
        if raw == "0":
            return None
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(items):
                return items[i - 1]
        console.print("Opción inválida.")


def _pick_status(default: str = "SCHEDULED") -> str:
    console.print("\nEstado del vuelo:")
    for idx, s in enumerate(FLIGHT_STATUSES, start=1):
        console.print(f"{idx}) {s}")
    console.print("0) Cancelar")

    while True:
        raw = input(f"Opción [{default}]: ").strip()
        if raw == "":
            return default
        if raw == "0":
            raise KeyboardInterrupt
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(FLIGHT_STATUSES):
                return FLIGHT_STATUSES[i - 1]

        if raw.upper() in FLIGHT_STATUSES:
            return raw.upper()
        console.print("Opción inválida.")


def _format_flight_row(
    f: dict[str, Any],
    airlines_map: dict[str, dict[str, Any]],
    airports_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    airline = airlines_map.get(str(f.get("airline_id")), {})
    origin = airports_map.get(str(f.get("origin_airport_id")), {})
    dest = airports_map.get(str(f.get("destination_airport_id")), {})

    airline_label = (
        airline.get("code") or airline.get("name") or str(f.get("airline_id"))
    )
    origin_code = origin.get("code") or str(f.get("origin_airport_id"))
    dest_code = dest.get("code") or str(f.get("destination_airport_id"))

    out = dict(f)
    out["airline_label"] = airline_label
    out["route"] = f"{origin_code} → {dest_code}"
    out["dep"] = _parse_dt(str(f.get("departure_at", "")))
    out["arr"] = _parse_dt(str(f.get("arrival_at", "")))
    return out


def flights_menu(client: APIClient) -> None:
    pretty: list[dict[str, Any]] = []
    airlines_map: dict[str, dict[str, Any]] = {}
    airports_map: dict[str, dict[str, Any]] = {}

    while True:
        clear_screen()
        console.print("=== VUELOS ===\n")
        console.print("1) Listar vuelos")
        console.print("2) Ver vuelo")
        console.print("3) Crear vuelo")
        console.print("4) Actualizar vuelo")
        console.print("5) Eliminar vuelo")
        console.print("0) Volver")
        console.print("----------------------")

        op = input("Opción: ").strip()

        try:
            if op == "0":
                return

            if op in {"1", "2", "4", "5"}:
                flights = list_flights(client)
                airlines_map = _build_id_map(list_airlines(client))
                airports_map = _build_id_map(list_airports(client))
                pretty = [
                    _format_flight_row(f, airlines_map, airports_map) for f in flights
                ]

            if op == "1":
                print_table(
                    pretty,
                    columns={
                        "flight_number": "Vuelo",
                        "airline_label": "Aerolínea",
                        "route": "Ruta",
                        "dep": "Salida",
                        "arr": "Llegada",
                        "status": "Estado",
                        "price_cop": "Precio (COP)",
                        "id": "ID",
                    },
                    title="Vuelos",
                    empty_message="No hay vuelos.",
                )
                pause()

            elif op == "2":
                if not pretty:
                    console.print("No hay vuelos.")
                    pause()
                    continue

                picked = _pick_from_list(
                    pretty,
                    title="Selecciona el vuelo:",
                    item_label=lambda x: (
                        f"{x.get('flight_number')} | {x.get('airline_label')} | "
                        f"{x.get('route')} | {x.get('dep')} → {x.get('arr')} | "
                        f"{x.get('status')} | COP {x.get('price_cop')}"
                    ),
                )
                if not picked:
                    continue

                f = get_flight(client, picked["id"])
                f_pretty = _format_flight_row(f, airlines_map, airports_map)
                print_table(
                    [f_pretty],
                    columns={
                        "flight_number": "Vuelo",
                        "airline_label": "Aerolínea",
                        "route": "Ruta",
                        "departure_at": "Salida (raw)",
                        "arrival_at": "Llegada (raw)",
                        "status": "Estado",
                        "price_cop": "Precio (COP)",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Vuelo",
                )
                pause()

            elif op == "3":
                clear_screen()
                console.print("=== Crear vuelo ===\n")

                airlines = list_airlines(client)
                airports = list_airports(client)

                if not airlines:
                    console.print("No hay aerolíneas creadas.")
                    pause()
                    continue
                if not airports:
                    console.print("No hay aeropuertos creados.")
                    pause()
                    continue

                picked_airline = _pick_from_list(
                    airlines,
                    title="Selecciona aerolínea:",
                    item_label=lambda a: f"{a.get('code')} | {a.get('name')}",
                )
                if not picked_airline:
                    continue

                picked_origin = _pick_from_list(
                    airports,
                    title="Selecciona aeropuerto ORIGEN:",
                    item_label=lambda a: (
                        f"{a.get('code')} | {a.get('name')} | {a.get('country')}"
                    ),
                )
                if not picked_origin:
                    continue

                picked_dest = _pick_from_list(
                    airports,
                    title="Selecciona aeropuerto DESTINO:",
                    item_label=lambda a: (
                        f"{a.get('code')} | {a.get('name')} | {a.get('country')}"
                    ),
                )
                if not picked_dest:
                    continue

                if str(picked_origin["id"]) == str(picked_dest["id"]):
                    console.print("\nOrigen y destino no pueden ser iguales.\n")
                    pause()
                    continue

                flight_number = input("Flight number (ej: AV123): ").strip()

                while True:
                    dep_raw = input("Salida (YYYY-MM-DD HH:MM): ").strip()
                    try:
                        departure_at = _parse_cli_datetime_to_iso(dep_raw)
                        break
                    except Exception:
                        console.print("Formato inválido. Ejemplo: 2026-03-10 10:00")

                while True:
                    arr_raw = input("Llegada (YYYY-MM-DD HH:MM): ").strip()
                    try:
                        arrival_at = _parse_cli_datetime_to_iso(arr_raw)
                        break
                    except Exception:
                        console.print("Formato inválido. Ejemplo: 2026-03-10 12:00")

                try:
                    status_value = _pick_status(default="SCHEDULED")
                except KeyboardInterrupt:
                    continue

                price_raw = input("Precio COP [150000]: ").strip() or "150000"

                payload: dict[str, Any] = {
                    "airline_id": picked_airline["id"],
                    "flight_number": flight_number,
                    "origin_airport_id": picked_origin["id"],
                    "destination_airport_id": picked_dest["id"],
                    "departure_at": departure_at,
                    "arrival_at": arrival_at,
                    "status": status_value,
                    "price_cop": int(price_raw),
                }

                created = create_flight(client, payload)
                console.print(
                    f"\nVuelo creado: {created['flight_number']} ({created['id']})\n"
                )
                pause()

            elif op == "4":
                if not pretty:
                    console.print("No hay vuelos.")
                    pause()
                    continue

                picked = _pick_from_list(
                    pretty,
                    title="Selecciona el vuelo a actualizar:",
                    item_label=lambda x: (
                        f"{x.get('flight_number')} | {x.get('airline_label')} | {x.get('route')}"
                    ),
                )
                if not picked:
                    continue

                current = get_flight(client, picked["id"])
                console.print("\nDeja vacío para mantener el valor actual.\n")

                flight_number = input(
                    f"Flight number [{current.get('flight_number')}]: "
                ).strip()

                dep_raw = input(
                    f"Salida (YYYY-MM-DD HH:MM) [{_parse_dt(str(current.get('departure_at')))}]: "
                ).strip()
                arr_raw = input(
                    f"Llegada (YYYY-MM-DD HH:MM) [{_parse_dt(str(current.get('arrival_at')))}]: "
                ).strip()

                console.print("\nEstado (elige o deja vacío para mantener):")
                for idx, s in enumerate(FLIGHT_STATUSES, start=1):
                    console.print(f"{idx}) {s}")
                status_raw = input(f"Opción [{current.get('status')}]: ").strip()

                price_raw = input(f"Precio COP [{current.get('price_cop')}]: ").strip()

                payload: dict[str, Any] = {}
                if flight_number:
                    payload["flight_number"] = flight_number
                if dep_raw:
                    payload["departure_at"] = _parse_cli_datetime_to_iso(dep_raw)
                if arr_raw:
                    payload["arrival_at"] = _parse_cli_datetime_to_iso(arr_raw)

                if status_raw:
                    if status_raw.isdigit():
                        i = int(status_raw)
                        if 1 <= i <= len(FLIGHT_STATUSES):
                            payload["status"] = FLIGHT_STATUSES[i - 1]
                    else:
                        payload["status"] = status_raw.upper()

                if price_raw != "":
                    payload["price_cop"] = int(price_raw)

                if not payload:
                    console.print("\nNo hay cambios.\n")
                    pause()
                    continue

                updated = update_flight(client, picked["id"], payload)
                console.print(
                    f"\nVuelo actualizado: {updated['flight_number']} ({updated['id']})\n"
                )
                pause()

            elif op == "5":
                if not pretty:
                    console.print("No hay vuelos.")
                    pause()
                    continue

                picked = _pick_from_list(
                    pretty,
                    title="Selecciona el vuelo a eliminar:",
                    item_label=lambda x: (
                        f"{x.get('flight_number')} | {x.get('airline_label')} | {x.get('route')}"
                    ),
                )
                if not picked:
                    continue

                confirm = (
                    input(f"¿Eliminar vuelo {picked.get('flight_number')}? (s/N): ")
                    .strip()
                    .lower()
                )
                if confirm != "s":
                    continue

                delete_flight(client, picked["id"])
                console.print("\nVuelo eliminado.\n")
                pause()

            else:
                console.print("Opción inválida.")
                pause()

        except Exception as exc:
            _handle_http_error(exc)
            pause()

from __future__ import annotations

from typing import Any

import httpx
from rich.console import Console

from datetime import datetime, timezone
from app.crud.airlines import list_airlines
from app.crud.airports import list_airports

from app.crud.http_client import APIClient
from app.crud.users import list_users
from app.crud.flights import list_flights
from app.crud.reservations import (
    create_reservation,
    get_reservation,
    list_reservations,
    update_reservation,
)
from app.crud.passengers import (
    create_passenger,
    delete_passenger,
    list_passengers_by_reservation,
)
from app.crud.reservation_flights import (
    create_reservation_flight,
    delete_reservation_flight,
    list_reservation_flights_by_reservation,
)
from app.utils.cli_utils import clear_screen, pause, print_table, get_validated_input

console = Console()


def _segment_label(segment_order: int) -> str:
    if segment_order == 1:
        return "Ida"
    if segment_order == 2:
        return "Vuelta"
    return f"Tramo {segment_order}"


def _parse_dt(value: str) -> str:
    try:
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return value


def _build_id_map(
    rows: list[dict[str, Any]], id_key: str = "id"
) -> dict[str, dict[str, Any]]:
    return {str(r[id_key]): r for r in rows}


def _users_map(client: APIClient) -> dict[str, dict[str, Any]]:
    users = list_users(client)
    return {str(u["id"]): u for u in users}


def _user_label(users_map: dict[str, dict[str, Any]], user_id: str) -> str:
    u = users_map.get(str(user_id))
    if not u:
        return str(user_id)
    full_name = u.get("full_name") or ""
    email = u.get("email") or ""
    return f"{full_name} ({email})".strip()


def _format_flight_option(
    flight: dict[str, Any],
    airlines_map: dict[str, dict[str, Any]],
    airports_map: dict[str, dict[str, Any]],
) -> str:
    airline = airlines_map.get(str(flight["airline_id"]), {})
    origin = airports_map.get(str(flight["origin_airport_id"]), {})
    dest = airports_map.get(str(flight["destination_airport_id"]), {})

    airline_label = airline.get("code") or airline.get("name") or "AIRLINE"
    origin_code = origin.get("code") or "ORG"
    dest_code = dest.get("code") or "DST"

    dep = _parse_dt(str(flight.get("departure_at", "")))
    arr = _parse_dt(str(flight.get("arrival_at", "")))
    number = flight.get("flight_number", "")
    status = flight.get("status", "")

    return f"{number} | {airline_label} | {origin_code} → {dest_code} | {dep} → {arr} | {status}"


def _handle_http_error(exc: Exception) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail")
        except Exception:
            detail = exc.response.text
        console.print(f"\n[red]HTTP {exc.response.status_code}[/red]: {detail}\n")
    else:
        console.print(f"\n[red]Error[/red]: {exc}\n")


def _pick_from_list(items: list[dict[str, Any]], label: str) -> dict[str, Any] | None:
    if not items:
        console.print("No hay datos para seleccionar.")
        return None

    for idx, it in enumerate(items, start=1):
        console.print(f"{idx}) {label.format(**it)}")

    console.print("0) Cancelar")
    while True:
        raw = input("Selecciona una opción: ").strip()
        if raw == "0":
            return None
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(items):
                return items[i - 1]
        console.print("Opción inválida.")


def _wizard_select_user(client: APIClient) -> dict[str, Any] | None:
    users = list_users(client)
    if not users:
        console.print("No hay usuarios creados.")
        pause()
        return None

    clear_screen()
    console.print("=== Selecciona el usuario comprador ===|")

    console.print("\nSelecciona por número:")
    for idx, u in enumerate(users, start=1):
        console.print(f"{idx}) {u.get('full_name')} ({u.get('email')})")

    console.print("0) Cancelar")
    while True:
        raw = input("Opción: ").strip()
        if raw == "0":
            return None
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(users):
                return users[i - 1]
        console.print("Opción inválida.")


def _wizard_create_reservation(client: APIClient) -> dict[str, Any] | None:
    user = _wizard_select_user(client)
    if not user:
        return None

    payload = {"user_id": user["id"], "status": "HOLD", "total_amount_cop": 0}
    res = create_reservation(client, payload)
    console.print(f"\nReserva creada: {res['id']} (status={res['status']})\n")
    return res


def _wizard_add_flights(client: APIClient, reservation_id: str) -> None:
    clear_screen()
    console.print("=== Agregar vuelos ===\n")

    console.print("Tipo de viaje:")
    console.print("1) Solo ida")
    console.print("2) Ida y vuelta")
    console.print("0) Cancelar\n")

    trip_type = get_validated_input("Opción", ["1", "2", "0"], default="1")
    if trip_type == "0":
        return

    flights = list_flights(client)
    if not flights:
        console.print("No hay vuelos creados aún.")
        pause()
        return

    airlines_map = _build_id_map(list_airlines(client))
    airports_map = _build_id_map(list_airports(client))

    def pick_flight(title: str) -> dict[str, Any] | None:
        console.print(f"\n{title}\n")

        for idx, f in enumerate(flights, start=1):
            console.print(
                f"{idx}) {_format_flight_option(f, airlines_map, airports_map)}"
            )

        console.print("0) Cancelar")
        while True:
            raw = input("Selecciona una opción: ").strip()
            if raw == "0":
                return None
            if raw.isdigit():
                i = int(raw)
                if 1 <= i <= len(flights):
                    return flights[i - 1]
            console.print("Opción inválida.")

    f1 = pick_flight("Selecciona el vuelo de ida")
    if not f1:
        return

    create_reservation_flight(
        client,
        reservation_id=reservation_id,
        flight_id=str(f1["id"]),
        segment_order=1,
    )
    console.print("\nVuelo de ida agregado.\n")

    if trip_type == "2":
        f2 = pick_flight("Selecciona el vuelo de vuelta")
        if not f2:
            return

        create_reservation_flight(
            client,
            reservation_id=reservation_id,
            flight_id=str(f2["id"]),
            segment_order=2,
        )
        console.print("\nVuelo de vuelta agregado.\n")

    pause()


def _view_itinerary(client: APIClient, reservation_id: str) -> None:
    items = list_reservation_flights_by_reservation(client, reservation_id)

    if not items:
        console.print("La reserva aún no tiene vuelos asociados.")
        pause()
        return

    # Lookups para convertir IDs a datos humanos
    flights = list_flights(client)
    flights_by_id = {str(f["id"]): f for f in flights}

    airlines_map = _build_id_map(list_airlines(client))
    airports_map = _build_id_map(list_airports(client))

    pretty_items: list[dict[str, Any]] = []
    for it in items:
        row = dict(it)

        # "Ida/Vuelta" en vez de segment_order
        row["trip_leg"] = _segment_label(int(it.get("segment_order", 0)))

        # Mostrar el vuelo en formato humano (no UUID)
        flight = flights_by_id.get(str(it["flight_id"]))
        if flight:
            row["flight_display"] = _format_flight_option(
                flight, airlines_map, airports_map
            )
        else:
            row["flight_display"] = str(it["flight_id"])

        pretty_items.append(row)

    print_table(
        pretty_items,
        columns={
            "trip_leg": "Tramo",
            "flight_display": "Vuelo",
        },
        title="Itinerario",
    )
    pause()


def _delete_itinerary_item(client: APIClient, reservation_id: str) -> None:
    items = list_reservation_flights_by_reservation(client, reservation_id)
    if not items:
        console.print("No hay vuelos asociados para eliminar.")
        pause()
        return

    console.print("\nSelecciona el segmento a eliminar:\n")
    picked = _pick_from_list(
        items,
        label="Tramo {segment_order} | flight_id={flight_id} | rel_id={id}",
    )
    if not picked:
        return

    delete_reservation_flight(client, picked["id"])
    console.print("\nSegmento eliminado.\n")
    pause()


def _view_passengers(client: APIClient, reservation_id: str) -> None:
    rows = list_passengers_by_reservation(client, reservation_id)
    print_table(
        rows,
        columns={
            "id": "ID",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "document_number": "Documento",
            "birth_date": "Nacimiento",
            "created_at": "Creado",
        },
        title="Pasajeros",
        empty_message="La reserva aún no tiene pasajeros.",
    )
    pause()


def _add_passenger(client: APIClient, reservation_id: str) -> None:
    clear_screen()
    console.print("=== Agregar pasajero ===\n")
    first_name = input("Nombre: ").strip()
    last_name = input("Apellido: ").strip()
    document_number = input("Documento: ").strip()
    birth_date = input("Nacimiento (YYYY-MM-DD) opcional: ").strip()

    payload: dict[str, Any] = {
        "reservation_id": reservation_id,
        "first_name": first_name,
        "last_name": last_name,
        "document_number": document_number,
    }
    if birth_date:
        payload["birth_date"] = birth_date

    created = create_passenger(
        client,
        reservation_id=reservation_id,
        first_name=first_name,
        last_name=last_name,
        document_number=document_number,
        birth_date=birth_date or None,
    )
    console.print(f"\nPasajero creado: {created['id']}\n")
    pause()


def _delete_passenger(client: APIClient, reservation_id: str) -> None:
    rows = list_passengers_by_reservation(client, reservation_id)
    if not rows:
        console.print("No hay pasajeros para eliminar.")
        pause()
        return

    console.print("\nSelecciona el pasajero a eliminar:\n")
    picked = _pick_from_list(
        rows,
        label="{first_name} {last_name} | doc={document_number} | id={id}",
    )
    if not picked:
        return

    delete_passenger(client, picked["id"])
    console.print("\nPasajero eliminado.\n")
    pause()


def _confirm_or_cancel(
    client: APIClient, reservation_id: str, status_value: str
) -> None:
    # Reglas mínimas "de negocio" para demo:
    # - Para confirmar: debe tener al menos 1 vuelo + 1 pasajero
    if status_value == "CONFIRMED":
        flights = list_reservation_flights_by_reservation(client, reservation_id)
        passengers = list_passengers_by_reservation(client, reservation_id)
        if not flights:
            console.print("\nNo puedes confirmar: faltan vuelos asociados.\n")
            pause()
            return
        if not passengers:
            console.print("\nNo puedes confirmar: faltan pasajeros.\n")
            pause()
            return

    updated = update_reservation(client, reservation_id, {"status": status_value})
    console.print(f"\nReserva actualizada: status={updated['status']}\n")
    pause()


def _manage_reservation(client: APIClient, reservation_id: str) -> None:
    while True:
        clear_screen()
        res = get_reservation(client, reservation_id)

        u_map = _users_map(client)
        user_display = _user_label(u_map, str(res["user_id"]))

        console.print("=== Gestionar reserva ===\n")
        console.print(f"Reserva:   {res['id']}")
        console.print(f"Usuario:   {user_display}")
        console.print(f"Estado:    {res['status']}")
        console.print(f"Total COP: {res['total_amount_cop']}")
        console.print("")

        console.print("1) Ver itinerario (vuelos)")
        console.print("2) Agregar vuelos")
        console.print("3) Eliminar un vuelo de la reserva")
        console.print("4) Ver pasajeros")
        console.print("5) Agregar pasajero")
        console.print("6) Eliminar pasajero")
        console.print("7) Confirmar reserva")
        console.print("8) Cancelar reserva")
        console.print("0) Volver")
        console.print("----------------------")

        op = input("Opción: ").strip()

        try:
            if op == "0":
                return
            if op == "1":
                clear_screen()
                _view_itinerary(client, reservation_id)
            elif op == "2":
                _wizard_add_flights(client, reservation_id)
            elif op == "3":
                clear_screen()
                _delete_itinerary_item(client, reservation_id)
            elif op == "4":
                clear_screen()
                _view_passengers(client, reservation_id)
            elif op == "5":
                _add_passenger(client, reservation_id)
            elif op == "6":
                clear_screen()
                _delete_passenger(client, reservation_id)
            elif op == "7":
                _confirm_or_cancel(client, reservation_id, "CONFIRMED")
            elif op == "8":
                _confirm_or_cancel(client, reservation_id, "CANCELED")
            else:
                console.print("Opción inválida.")
                pause()
        except Exception as exc:
            _handle_http_error(exc)
            pause()


def reservations_menu(client: APIClient) -> None:
    pretty_rows: list[dict[str, Any]]

    while True:
        clear_screen()
        console.print("=== RESERVAS (Flujo de compra) ===\n")
        console.print("1) Listar reservas")
        console.print("2) Crear reserva")
        console.print("3) Gestionar reserva")
        console.print("0) Salir")
        console.print("----------------------")

        op = input("Opción: ").strip()

        try:
            if op == "0":
                return

            if op == "1":
                rows = list_reservations(client)
                u_map = _users_map(client)

                pretty_rows = []
                for r in rows:
                    rr = dict(r)
                    rr["user_display"] = _user_label(u_map, str(r["user_id"]))
                    pretty_rows.append(rr)

                print_table(
                    pretty_rows,
                    columns={
                        "id": "ID",
                        "user_display": "Usuario",
                        "status": "Estado",
                        "total_amount_cop": "Total (COP)",
                        "created_at": "Creado",
                    },
                    title="Reservas",
                    empty_message="No hay reservas.",
                )
                pause()

            elif op == "2":
                clear_screen()
                created = _wizard_create_reservation(client)
                if created:
                    # entra directo a gestionar (flujo real)
                    _manage_reservation(client, created["id"])

            elif op == "3":
                rows = list_reservations(client)
                if not rows:
                    console.print("No hay reservas.")
                    pause()
                    continue

                u_map = _users_map(client)

                # Tabla con usuario humano
                pretty_rows = []
                for r in rows:
                    rr = dict(r)
                    rr["user_display"] = _user_label(u_map, str(r["user_id"]))
                    pretty_rows.append(rr)

                clear_screen()

                console.print("\nSelecciona por número:")
                for idx, r in enumerate(pretty_rows, start=1):
                    console.print(
                        f"{idx}) {r['status']} | {r['user_display']} | {r['id']}"
                    )

                console.print("0) Cancelar")
                while True:
                    raw = input("Opción: ").strip()
                    if raw == "0":
                        break
                    if raw.isdigit():
                        i = int(raw)
                        if 1 <= i <= len(pretty_rows):
                            _manage_reservation(client, pretty_rows[i - 1]["id"])
                            break
                    console.print("Opción inválida.")

            else:
                console.print("Opción inválida.")
                pause()

        except Exception as exc:
            _handle_http_error(exc)
            pause()

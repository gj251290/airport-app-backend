from __future__ import annotations

from typing import Any

import httpx
from rich.console import Console

from app.crud.http_client import APIClient
from app.crud.users import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)
from app.utils.cli_utils import clear_screen, pause, print_table

console = Console()

USER_ROLES = ["CLIENT", "ADMIN"]  # opcional: puedes dejarlo libre si quieres


def _handle_http_error(exc: Exception) -> None:
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail")
        except Exception:
            detail = exc.response.text
        console.print(f"\n[red]HTTP {exc.response.status_code}[/red]: {detail}\n")
    else:
        console.print(f"\n[red]Error[/red]: {exc}\n")


def _pick_from_list(items: list[dict[str, Any]], title: str) -> dict[str, Any] | None:
    if not items:
        console.print("No hay datos para seleccionar.")
        return None

    console.print(f"{title}\n")
    for idx, u in enumerate(items, start=1):
        console.print(
            f"{idx}) {u.get('full_name')} | {u.get('email')} | {u.get('role')}"
        )
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


def _pick_role(default: str = "CLIENT") -> str:
    console.print("\nRol:")
    for idx, r in enumerate(USER_ROLES, start=1):
        console.print(f"{idx}) {r}")
    console.print("0) Cancelar")

    while True:
        raw = input(f"Opción [{default}]: ").strip()
        if raw == "":
            return default
        if raw == "0":
            raise KeyboardInterrupt

        # permitir por número
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(USER_ROLES):
                return USER_ROLES[i - 1]

        # permitir escribir el texto
        up = raw.upper()
        if up in USER_ROLES:
            return up

        console.print("Opción inválida.")


def users_menu(client: APIClient) -> None:
    while True:
        clear_screen()
        console.print("=== USUARIOS ===\n")
        console.print("1) Listar usuarios")
        console.print("2) Ver usuario")
        console.print("3) Crear usuario")
        console.print("4) Actualizar usuario")
        console.print("5) Eliminar usuario")
        console.print("0) Volver")
        console.print("----------------------")

        op = input("Opción: ").strip()

        try:
            if op == "0":
                return

            if op == "1":
                rows = list_users(client)
                print_table(
                    rows,
                    columns={
                        "full_name": "Nombre",
                        "email": "Email",
                        "role": "Rol",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Usuarios",
                    empty_message="No hay usuarios.",
                )
                pause()

            elif op == "2":
                rows = list_users(client)
                if not rows:
                    console.print("No hay usuarios.")
                    pause()
                    continue

                picked = _pick_from_list(rows, "Selecciona el usuario:")
                if not picked:
                    continue

                u = get_user(client, picked["id"])
                print_table(
                    [u],
                    columns={
                        "full_name": "Nombre",
                        "email": "Email",
                        "role": "Rol",
                        "id": "ID",
                        "created_at": "Creado",
                    },
                    title="Usuario",
                )
                pause()

            elif op == "3":
                clear_screen()
                console.print("=== Crear usuario ===\n")
                email = input("Email: ").strip()
                full_name = input("Nombre completo: ").strip()

                try:
                    role = _pick_role(default="CLIENT")
                except KeyboardInterrupt:
                    continue

                payload: dict[str, Any] = {
                    "email": email,
                    "full_name": full_name,
                    "role": role,
                }
                created = create_user(client, payload)
                console.print(
                    f"\nUsuario creado: {created['full_name']} ({created['id']})\n"
                )
                pause()

            elif op == "4":
                rows = list_users(client)
                if not rows:
                    console.print("No hay usuarios.")
                    pause()
                    continue

                picked = _pick_from_list(rows, "Selecciona el usuario a actualizar:")
                if not picked:
                    continue

                current = get_user(client, picked["id"])
                clear_screen()
                console.print("=== Actualizar usuario ===\n")
                console.print("Deja vacío para mantener el valor actual.\n")

                email = input(f"Email [{current.get('email')}]: ").strip()
                full_name = input(
                    f"Nombre completo [{current.get('full_name')}]: "
                ).strip()

                change_role = input("¿Cambiar rol? (s/N): ").strip().lower()
                role_value: str | None = None
                if change_role == "s":
                    try:
                        role_value = _pick_role(default=current.get("role") or "CLIENT")
                    except KeyboardInterrupt:
                        role_value = None

                payload: dict[str, Any] = {}
                if email:
                    payload["email"] = email
                if full_name:
                    payload["full_name"] = full_name
                if role_value is not None:
                    payload["role"] = role_value

                if not payload:
                    console.print("\nNo hay cambios.\n")
                    pause()
                    continue

                updated = update_user(client, picked["id"], payload)
                console.print(
                    f"\nUsuario actualizado: {updated['full_name']} ({updated['id']})\n"
                )
                pause()

            elif op == "5":
                rows = list_users(client)
                if not rows:
                    console.print("No hay usuarios.")
                    pause()
                    continue

                picked = _pick_from_list(rows, "Selecciona el usuario a eliminar:")
                if not picked:
                    continue

                confirm = (
                    input(
                        f"¿Eliminar {picked.get('full_name')} ({picked.get('email')})? (s/N): "
                    )
                    .strip()
                    .lower()
                )
                if confirm != "s":
                    continue

                delete_user(client, picked["id"])
                console.print("\nUsuario eliminado.\n")
                pause()

            else:
                console.print("Opción inválida.")
                pause()

        except Exception as exc:
            _handle_http_error(exc)
            pause()

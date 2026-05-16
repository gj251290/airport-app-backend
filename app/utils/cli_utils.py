from __future__ import annotations

from typing import Any, Iterable

import os

from rich.console import Console
from rich.table import Table

console = Console()


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause(message: str = "Presiona Enter para continuar...") -> None:
    input(message)


def print_table(
    rows: list[dict[str, Any]],
    *,
    columns: dict[str, str],
    title: str | None = None,
    empty_message: str = "No hay registros.",
) -> None:
    if not rows:
        console.print(empty_message)
        return

    table = Table(title=title)
    for key, header in columns.items():
        table.add_column(header)

    for row in rows:
        values: list[str] = []
        for key in columns.keys():
            v = row.get(key)
            values.append("" if v is None else str(v))
        table.add_row(*values)

    console.print(table)


def get_validated_input(
    prompt: str,
    valid_options: Iterable[str],
    default: str | None = None,
) -> str:
    valid = [str(x) for x in valid_options]

    while True:
        suffix = ""
        if default is not None:
            suffix = f" [{default}]"

        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default is not None:
            return default

        if value in valid:
            return value

        console.print(f"Opción inválida. Opciones válidas: {', '.join(valid)}")

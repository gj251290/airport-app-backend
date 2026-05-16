"""Migracion inicial completa

Revision ID: 53c3ac11e09c
Revises:
Create Date: 2026-03-27 21:55:16.338737

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "53c3ac11e09c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. CREACIÓN DE TABLAS BASE
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column(
            "role", sa.String(length=16), server_default="CLIENT", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "airlines",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("country", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "airports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("country", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # 2. TABLAS CON DEPENDENCIAS
    op.create_table(
        "flights",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("airline_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flight_number", sa.Text(), nullable=False),
        sa.Column("origin_airport_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "destination_airport_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("departure_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="SCHEDULED"),
        sa.Column("price_cop", sa.Integer(), nullable=False, server_default="150000"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["airline_id"],
            ["airlines.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_airport_id"],
            ["airports.id"],
        ),
        sa.ForeignKeyConstraint(
            ["origin_airport_id"],
            ["airports.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "airline_id", "flight_number", "departure_at", name="uq_flight_departure"
        ),
        sa.CheckConstraint(
            "origin_airport_id <> destination_airport_id",
            name="chk_flights_airports_different",
        ),
        sa.CheckConstraint("arrival_at > departure_at", name="chk_flights_time_order"),
    )

    op.create_table(
        "reservations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Text(), server_default="HOLD", nullable=False),
        sa.Column("total_amount_cop", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "passengers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("document_number", sa.Text(), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"],
            ["reservations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reservation_flights",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flight_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("segment_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["flight_id"],
            ["flights.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"],
            ["reservations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reservation_id", "flight_id", name="uq_reservation_flight"
        ),
        sa.UniqueConstraint(
            "reservation_id", "segment_order", name="uq_reservation_segment"
        ),
    )


def downgrade() -> None:
    op.drop_table("reservation_flights")
    op.drop_table("passengers")
    op.drop_table("reservations")
    op.drop_table("flights")
    op.drop_table("airports")
    op.drop_table("airlines")
    op.drop_table("users")

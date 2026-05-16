"""add password_hash to users

Revision ID: a7f3d4c92b10
Revises: 53c3ac11e09c
Create Date: 2026-04-07 20:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a7f3d4c92b10"
down_revision: Union[str, Sequence[str], None] = "53c3ac11e09c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.Text(),
            nullable=False,
            server_default="DISABLED_PASSWORD_HASH",
        ),
    )
    op.alter_column("users", "password_hash", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "password_hash")

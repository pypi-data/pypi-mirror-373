"""add lookup defaults

Peek Plugin Database Migration Script

Revision ID: 00ac445cc5c3
Revises: 2ed16c3ccc6a
Create Date: 2025-03-05 17:32:31.186645

"""

# revision identifiers, used by Alembic.
revision = "00ac445cc5c3"
down_revision = "2ed16c3ccc6a"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    for table in (
        "DispLayer",
        "DispLevel",
        "DispTextStyle",
        "DispLineStyle",
        "DispColor",
    ):
        for column in ("showForEdit", "blockApiUpdate"):
            op.alter_column(
                table,
                column,
                type_=sa.Boolean(),
                server_default="false",
                schema="pl_diagram",
                nullable=False,
            )

    op.alter_column(
        "DispColor",
        "darkColor",
        type_=sa.String(),
        server_default="#FFA500",
        schema="pl_diagram",
        nullable=True,
    )

    op.alter_column(
        "DispColor",
        "lightColor",
        type_=sa.String(),
        server_default="#FF8C00",
        schema="pl_diagram",
        nullable=True,
    )

    op.alter_column(
        "DispColor",
        "altColor",
        type_=sa.String(),
        schema="pl_diagram",
        nullable=True,
    )

    # DispLineStyle

    op.alter_column(
        "DispLineStyle",
        "capStyle",
        type_=sa.String(),
        schema="pl_diagram",
        server_default="butt",
        nullable=False,
    )

    op.alter_column(
        "DispLineStyle",
        "joinStyle",
        type_=sa.String(),
        schema="pl_diagram",
        server_default="miter",
        nullable=False,
    )

    op.alter_column(
        "DispLineStyle",
        "winStyle",
        type_=sa.Integer(),
        schema="pl_diagram",
        server_default="1",
        nullable=False,
    )

    # DispLevel

    op.alter_column(
        "DispLevel",
        "order",
        type_=sa.Integer(),
        schema="pl_diagram",
        server_default="0",
        nullable=False,
    )

    op.alter_column(
        "DispLevel",
        "minZoom",
        type_=sa.Float(),
        schema="pl_diagram",
        server_default="0.5",
        nullable=False,
    )

    op.alter_column(
        "DispLevel",
        "maxZoom",
        type_=sa.Float(),
        schema="pl_diagram",
        server_default="1.5",
        nullable=False,
    )


def downgrade():
    pass

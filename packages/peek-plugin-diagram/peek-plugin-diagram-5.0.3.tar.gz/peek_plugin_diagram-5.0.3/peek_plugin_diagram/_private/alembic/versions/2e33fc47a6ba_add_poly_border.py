"""add poly border

Peek Plugin Database Migration Script

Revision ID: 2e33fc47a6ba
Revises: 2e676d2def0d
Create Date: 2025-05-15 21:42:49.696298

"""

# revision identifiers, used by Alembic.
revision = "2e33fc47a6ba"
down_revision = "2e676d2def0d"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "DispPolyline",
        sa.Column("borderWidth", sa.Integer, nullable=True),
        schema="pl_diagram",
    )
    op.add_column(
        "DispPolyline",
        sa.Column(
            "borderColorId",
            sa.Integer,
            sa.ForeignKey("DispColor.id"),
            nullable=True,
        ),
        schema="pl_diagram",
    )


def downgrade():
    op.drop_column("DispPolyline", "borderWidth", schema="pl_diagram")
    op.drop_column("DispPolyline", "borderColorId", schema="pl_diagram")

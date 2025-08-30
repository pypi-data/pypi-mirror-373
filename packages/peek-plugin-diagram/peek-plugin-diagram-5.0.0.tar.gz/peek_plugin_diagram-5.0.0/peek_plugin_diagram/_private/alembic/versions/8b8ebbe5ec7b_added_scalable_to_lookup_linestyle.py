"""added scalable to lookup linestyle

Peek Plugin Database Migration Script

Revision ID: 8b8ebbe5ec7b
Revises: 42a8dc25e588
Create Date: 2022-05-26 14:33:55.123311

"""

# revision identifiers, used by Alembic.
from sqlalchemy import Boolean

revision = "8b8ebbe5ec7b"
down_revision = "42a8dc25e588"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "DispLineStyle",
        sa.Column("scalable", Boolean, server_default="false"),
        schema="pl_diagram",
    )


def downgrade():
    op.drop_column("DispLineStyle", "scalable", schema="pl_diagram")

"""add coordset default mode

Peek Plugin Database Migration Script

Revision ID: 2ed16c3ccc6a
Revises: 1e2f86ad5915
Create Date: 2025-01-09 22:48:45.955608

"""

# revision identifiers, used by Alembic.
revision = "2ed16c3ccc6a"
down_revision = "1e2f86ad5915"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():

    op.add_column(
        "ModelCoordSet",
        sa.Column(
            "initialDarkMode",
            sa.Boolean(),
            server_default="true",
            nullable=True,
        ),
        schema="pl_diagram",
    )

    op.execute(
        'UPDATE "pl_diagram"."ModelCoordSet" SET "initialDarkMode" = true '
    )
    op.alter_column(
        "ModelCoordSet",
        "initialDarkMode",
        type_=sa.Boolean(),
        server_default="true",
        schema="pl_diagram",
        nullable=False,
    )


def downgrade():
    op.drop_column("ModelCoordSet", "initialDarkMode", schema="pl_diagram")

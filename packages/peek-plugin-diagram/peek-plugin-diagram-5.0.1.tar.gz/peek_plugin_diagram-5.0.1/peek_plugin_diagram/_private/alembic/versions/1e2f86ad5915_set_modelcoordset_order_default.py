"""set ModelCoordSet.order default

Peek Plugin Database Migration Script

Revision ID: 1e2f86ad5915
Revises: 18bd59a236c8
Create Date: 2024-10-22 18:56:42.900094

"""

# revision identifiers, used by Alembic.
revision = "1e2f86ad5915"
down_revision = "18bd59a236c8"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column(
        "ModelCoordSet",
        sa.Column("order", sa.Integer(), server_default="0", nullable=True),
        schema="pl_diagram",
    )


def downgrade():
    pass

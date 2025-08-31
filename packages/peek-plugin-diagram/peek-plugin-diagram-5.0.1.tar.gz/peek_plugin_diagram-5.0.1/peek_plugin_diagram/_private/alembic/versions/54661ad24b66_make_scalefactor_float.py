"""make scaleFactor float

Peek Plugin Database Migration Script

Revision ID: 54661ad24b66
Revises: 4e7cad4a0ff7
Create Date: 2025-07-25 14:17:10.476101

"""

# revision identifiers, used by Alembic.
revision = "54661ad24b66"
down_revision = "4e7cad4a0ff7"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():

    op.alter_column(
        "DispTextStyle",
        "scaleFactor",
        type_=sa.Float(),
        schema="pl_diagram",
        server_default="1.0",
        nullable=False,
    )


def downgrade():
    pass

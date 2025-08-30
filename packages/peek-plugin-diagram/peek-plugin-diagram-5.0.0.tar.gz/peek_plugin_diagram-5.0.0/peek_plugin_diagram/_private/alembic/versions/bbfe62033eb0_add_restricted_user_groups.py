"""add restricted user groups

Peek Plugin Database Migration Script

Revision ID: bbfe62033eb0
Revises: 8f4a204ef136
Create Date: 2024-03-28 06:30:56.318623

"""

# revision identifiers, used by Alembic.
revision = "bbfe62033eb0"
down_revision = "8f4a204ef136"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        table_name="ModelCoordSet",
        column=sa.Column("restrictedToUserGroups", sa.String(), nullable=True),
        schema="pl_diagram",
    )


def downgrade():
    op.drop_column(
        "ModelCoordSet", "restrictedToUserGroups", schema="pl_diagram"
    )

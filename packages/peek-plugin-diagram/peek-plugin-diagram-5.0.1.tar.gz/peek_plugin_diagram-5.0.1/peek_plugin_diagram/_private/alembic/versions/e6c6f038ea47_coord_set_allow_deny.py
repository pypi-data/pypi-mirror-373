"""coord set allow deny

Peek Plugin Database Migration Script

Revision ID: e6c6f038ea47
Revises: bbfe62033eb0
Create Date: 2024-06-26 13:39:38.632955

"""

# revision identifiers, used by Alembic.
revision = "e6c6f038ea47"
down_revision = "bbfe62033eb0"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column(
        "ModelCoordSet",
        "restrictedToUserGroups",
        schema="pl_diagram",
        nullable=True,
        new_column_name="userGroupsAllowed",
    )
    op.add_column(
        table_name="ModelCoordSet",
        column=sa.Column("userGroupsDenied", sa.String(), nullable=True),
        schema="pl_diagram",
    )


def downgrade():
    op.drop_column("ModelCoordSet", "userGroupsDenied", schema="pl_diagram")

    op.alter_column(
        "ModelCoordSet",
        "userGroupsAllowed",
        schema="pl_diagram",
        nullable=True,
        new_column_name="restrictedToUserGroups",
    )

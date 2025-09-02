"""add canvas order

Peek Plugin Database Migration Script

Revision ID: 18bd59a236c8
Revises: e6c6f038ea47
Create Date: 2024-07-31 18:57:08.800754

"""

# revision identifiers, used by Alembic.
revision = "18bd59a236c8"
down_revision = "e6c6f038ea47"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "ModelCoordSet",
        sa.Column("order", sa.Integer(), nullable=True, server_default="1000"),
        schema="pl_diagram",
    )

    op.execute(
        """
        WITH numbered AS (
            SELECT *, ROW_NUMBER() OVER (ORDER BY name) AS num
            FROM pl_diagram."ModelCoordSet"
        )
        UPDATE pl_diagram."ModelCoordSet" t1
        SET "order" = (n.num + 1) * 10
        FROM numbered n
        WHERE n.id = t1.id
    """
    )

    op.execute(
        """
        UPDATE pl_diagram."ModelCoordSet"
        SET "order" = 0
        WHERE id in (
            SELECT "landingCoordSetId" FROM pl_diagram."ModelSet"
        )
    """
    )

    op.alter_column(
        "ModelCoordSet",
        "order",
        existing_type=sa.Integer(),
        nullable=False,
        schema="pl_diagram",
    )

    op.drop_column("ModelSet", "landingCoordSetId", schema="pl_diagram")


def downgrade():
    raise Exception("Downgrade is not supported")

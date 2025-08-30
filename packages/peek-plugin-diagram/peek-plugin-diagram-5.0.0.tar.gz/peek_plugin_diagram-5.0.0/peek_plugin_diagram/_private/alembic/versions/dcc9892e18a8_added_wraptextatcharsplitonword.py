"""added wrapTextAtCharSplitBetweenWords

Peek Plugin Database Migration Script

Revision ID: dcc9892e18a8
Revises: a151fd42572b
Create Date: 2023-08-04 09:51:29.490205

"""

# revision identifiers, used by Alembic.
revision = "dcc9892e18a8"
down_revision = "a151fd42572b"
branch_labels = None
depends_on = None

from alembic import (
    op,
)
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.add_column(
        "DispTextStyle",
        sa.Column(
            "wrapTextAtCharSplitBetweenWords",
            sa.Boolean(),
            server_default="true",
            nullable=True,
        ),
        schema="pl_diagram",
    )

    op.execute(
        """
        UPDATE pl_diagram."DispTextStyle"
        SET "wrapTextAtCharSplitBetweenWords" = true
        WHERE "wrapTextAtCharSplitBetweenWords" is null;
    """
    )

    op.alter_column(
        "DispTextStyle",
        "wrapTextAtCharSplitBetweenWords",
        nullable=False,
        schema="pl_diagram",
    )


def downgrade():
    op.drop_column(
        "DispTextStyle",
        "wrapTextAtCharSplitBetweenWords",
        schema="pl_diagram",
    )

"""remove name field limit

Peek Plugin Database Migration Script

Revision ID: 8f4a204ef136
Revises: bc5c2281bcee
Create Date: 2023-10-19 09:39:38.628212

"""

# revision identifiers, used by Alembic.
revision = "8f4a204ef136"
down_revision = "bc5c2281bcee"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column(
        "DispLayer",
        "name",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispLevel",
        "name",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispTextStyle",
        "name",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispTextStyle",
        "fontName",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispTextStyle",
        "fontStyle",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispLineStyle",
        "name",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispLineStyle",
        "dashPattern",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )

    op.alter_column(
        "DispColor",
        "name",
        type_=sa.String(),
        nullable=True,
        schema="pl_diagram",
    )


def downgrade():
    pass

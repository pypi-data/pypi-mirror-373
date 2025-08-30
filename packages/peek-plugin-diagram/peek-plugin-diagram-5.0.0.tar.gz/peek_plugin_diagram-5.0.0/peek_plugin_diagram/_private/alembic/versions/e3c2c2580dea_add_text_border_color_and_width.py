"""add text border color and width

Peek Plugin Database Migration Script

Revision ID: e3c2c2580dea
Revises: 47879bec4c5f
Create Date: 2022-07-06 10:37:27.196092

"""

# revision identifiers, used by Alembic.
revision = "e3c2c2580dea"
down_revision = "47879bec4c5f"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # add DispText.borderColorId and the foreign key
    op.add_column(
        "DispText",
        sa.Column("borderColorId", sa.Integer(), nullable=True),
        schema="pl_diagram",
    )
    op.create_foreign_key(
        "DispText_borderColorId_fkey",
        "DispText",
        "DispColor",
        ["borderColorId"],
        ["id"],
        source_schema="pl_diagram",
        referent_schema="pl_diagram",
    )

    # add DispTextStyle.borderWidth
    op.add_column(
        "DispTextStyle",
        sa.Column("borderWidth", sa.Float(), nullable=True),
        schema="pl_diagram",
    )


def downgrade():
    # drop DispText.borderColorId and the foreign key
    op.drop_constraint(
        "DispText_borderColorId_fkey", "DispText", schema="pl_diagram"
    )
    op.drop_column("DispText", "borderColorId", schema="pl_diagram")

    # drop DispTextStyle.borderWidth
    op.drop_column("DispTextStyle", "borderWidth", schema="pl_diagram")

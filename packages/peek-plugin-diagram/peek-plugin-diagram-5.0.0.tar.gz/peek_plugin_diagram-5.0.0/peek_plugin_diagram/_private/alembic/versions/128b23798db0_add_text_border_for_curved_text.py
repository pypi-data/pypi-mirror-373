"""add text border for curved text

Peek Plugin Database Migration Script

Revision ID: 128b23798db0
Revises: e3c2c2580dea
Create Date: 2022-07-07 13:51:54.645086

"""

# revision identifiers, used by Alembic.
revision = "128b23798db0"
down_revision = "e3c2c2580dea"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # add DispText.borderColorId and the foreign key
    op.add_column(
        "DispCurvedText",
        sa.Column("borderColorId", sa.Integer(), nullable=True),
        schema="pl_diagram",
    )
    op.create_foreign_key(
        "DispCurvedText_borderColorId_fkey",
        "DispCurvedText",
        "DispColor",
        ["borderColorId"],
        ["id"],
        source_schema="pl_diagram",
        referent_schema="pl_diagram",
    )


def downgrade():
    # drop DispText.borderColorId and the foreign key
    op.drop_constraint(
        "DispCurvedText_borderColorId_fkey",
        "DispCurvedText",
        schema="pl_diagram",
    )
    op.drop_column("DispCurvedText", "borderColorId", schema="pl_diagram")

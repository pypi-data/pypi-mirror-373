"""added curved text disp

Peek Plugin Database Migration Script

Revision ID: a4c59bcaaf88
Revises: 8b8ebbe5ec7b
Create Date: 2022-05-27 14:30:03.965868

"""

# revision identifiers, used by Alembic.
revision = "a4c59bcaaf88"
down_revision = "8b8ebbe5ec7b"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "DispCurvedText",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column(
            "verticalAlign", sa.Integer(), server_default="-1", nullable=False
        ),
        sa.Column(
            "horizontalAlign", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column(
            "text", sa.String(), server_default="new text label", nullable=True
        ),
        sa.Column("textHeight", sa.Float(), nullable=True),
        sa.Column("geomJson", sa.String(), nullable=False),
        sa.Column("colorId", sa.Integer(), nullable=True),
        sa.Column("textStyleId", sa.Integer(), nullable=False),
        sa.Column(
            "spacingBetweenTexts",
            sa.Float(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["colorId"],
            ["pl_diagram.DispColor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"], ["pl_diagram.DispBase.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["textStyleId"],
            ["pl_diagram.DispTextStyle.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pl_diagram",
    )


def downgrade():
    op.drop_table("DispCurvedText", schema="pl_diagram")

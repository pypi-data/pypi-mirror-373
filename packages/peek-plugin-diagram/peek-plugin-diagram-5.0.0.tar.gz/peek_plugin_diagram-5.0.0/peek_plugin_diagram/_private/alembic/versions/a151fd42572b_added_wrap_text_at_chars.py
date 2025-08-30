"""added wrap text at chars

Peek Plugin Database Migration Script

Revision ID: a151fd42572b
Revises: 57e88ad9d5cb
Create Date: 2023-03-16 10:46:57.388587

"""

# revision identifiers, used by Alembic.
revision = "a151fd42572b"
down_revision = "57e88ad9d5cb"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        table_name="DispTextStyle",
        column=sa.Column("wrapTextAtChars", sa.Integer(), nullable=True),
        schema="pl_diagram",
    )


def downgrade():
    op.drop_column(
        table_name="DispTextStyle",
        column_name="wrapTextAtChars",
        schema="pl_diagram",
    )

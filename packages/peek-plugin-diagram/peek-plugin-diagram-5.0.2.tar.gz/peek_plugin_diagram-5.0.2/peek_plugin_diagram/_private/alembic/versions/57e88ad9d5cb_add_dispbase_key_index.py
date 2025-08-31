"""add DispBase.key index

Peek Plugin Database Migration Script

Revision ID: 57e88ad9d5cb
Revises: 0ad02369aaea
Create Date: 2023-02-20 14:07:57.536490

"""

# revision identifiers, used by Alembic.
revision = "57e88ad9d5cb"
down_revision = "0ad02369aaea"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.create_index(
        "idx_Disp_key", "DispBase", ["key"], unique=False, schema="pl_diagram"
    )


def downgrade():
    op.drop_index("idx_Disp_key", table_name="DispBase", schema="pl_diagram")

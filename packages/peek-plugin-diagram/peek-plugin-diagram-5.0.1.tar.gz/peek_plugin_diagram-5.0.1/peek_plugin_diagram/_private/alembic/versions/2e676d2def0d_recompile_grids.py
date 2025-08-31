"""recompile grids

Peek Plugin Database Migration Script

Revision ID: 2e676d2def0d
Revises: 9b918f262551
Create Date: 2025-05-15 09:40:45.814891

"""

# revision identifiers, used by Alembic.
revision = "2e676d2def0d"
down_revision = "9b918f262551"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.execute(
        """
        insert into pl_diagram."GridKeyCompilerQueue"
        ("coordSetId" , "gridKey")
        select "coordSetId", "gridKey"
        FROM pl_diagram."GridKeyIndexCompiled"
        """
    )


def downgrade():
    pass

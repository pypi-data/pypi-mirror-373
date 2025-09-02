"""fix dispId bigint

Peek Plugin Database Migration Script

Revision ID: 9b918f262551
Revises: 00ac445cc5c3
Create Date: 2025-03-11 09:16:45.372359

"""

# revision identifiers, used by Alembic.
revision = "9b918f262551"
down_revision = "00ac445cc5c3"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.execute(
        """
            ALTER TABLE "pl_diagram"."DispCompilerQueue"
            ALTER COLUMN "dispId" TYPE bigint;
            
            ALTER TABLE "pl_diagram"."DispGroupPointer"
            ALTER COLUMN "targetDispGroupId" TYPE bigint;
            
            ALTER TABLE "pl_diagram"."DispPolyline"
            ALTER COLUMN "targetEdgeTemplateId" TYPE bigint;
        """
    )


def downgrade():
    pass

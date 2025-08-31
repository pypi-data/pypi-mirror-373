"""del unused ct fields

Peek Plugin Database Migration Script

Revision ID: 9cf78bdbbb2e
Revises: 2e33fc47a6ba
Create Date: 2025-05-18 12:43:34.333953

"""

# revision identifiers, used by Alembic.
revision = "9cf78bdbbb2e"
down_revision = "2e33fc47a6ba"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # Drop the unused columns from DispCurvedText table
    op.drop_column("DispCurvedText", "verticalAlign", schema="pl_diagram")
    op.drop_column("DispCurvedText", "horizontalAlign", schema="pl_diagram")
    op.drop_column("DispCurvedText", "textHeight", schema="pl_diagram")
    op.drop_column("DispCurvedText", "textHStretch", schema="pl_diagram")

    # Update the server default for spacingBetweenTexts in DispCurvedText table
    op.alter_column(
        "DispCurvedText",
        "spacingBetweenTexts",
        schema="pl_diagram",
        server_default=sa.text("100"),
        existing_type=sa.Float(),
    )


def downgrade():
    # Re-add the columns if downgrading
    op.add_column(
        "DispCurvedText",
        sa.Column(
            "verticalAlign",
            sa.INTEGER(),
            server_default=sa.text("-1"),
            nullable=False,
        ),
        schema="pl_diagram",
    )
    op.add_column(
        "DispCurvedText",
        sa.Column(
            "horizontalAlign",
            sa.INTEGER(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        schema="pl_diagram",
    )
    op.add_column(
        "DispCurvedText",
        sa.Column("textHeight", sa.FLOAT(), nullable=True),
        schema="pl_diagram",
    )
    op.add_column(
        "DispCurvedText",
        sa.Column(
            "textHStretch",
            sa.FLOAT(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        schema="pl_diagram",
    )

"""add layer parents

Peek Plugin Database Migration Script

Revision ID: 4e7cad4a0ff7
Revises: 9cf78bdbbb2e
Create Date: 2025-06-30 19:52:32.690555

"""

# revision identifiers, used by Alembic.
revision = "4e7cad4a0ff7"
down_revision = "9cf78bdbbb2e"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    # Add parentId column
    op.add_column(
        "DispLayer",
        sa.Column("parentId", sa.Integer(), nullable=True),
        schema="pl_diagram",
    )

    # Add foreign key constraint for parentId
    op.create_foreign_key(
        "fk_DispLayer_parentId",
        "DispLayer",
        "DispLayer",
        ["parentId"],
        ["id"],
        ondelete="CASCADE",
        source_schema="pl_diagram",
        referent_schema="pl_diagram",
    )

    # Add editorVisible and editorEditable columns
    op.add_column(
        "DispLayer",
        sa.Column("editorVisible", sa.Boolean(), nullable=True),
        schema="pl_diagram",
    )

    op.add_column(
        "DispLayer",
        sa.Column("editorEditable", sa.Boolean(), nullable=True),
        schema="pl_diagram",
    )

    # Make visible and selectable nullable (inherit from parent when null)
    op.alter_column("DispLayer", "visible", nullable=True, schema="pl_diagram")
    op.alter_column(
        "DispLayer", "selectable", nullable=True, schema="pl_diagram"
    )

    # Create parent layers for common import types
    op.execute(
        """
        INSERT INTO pl_diagram."DispLayer" ("name", "order", "visible", "selectable", "opacity", "modelSetId", "importHash", "showForEdit", "blockApiUpdate", "editorVisible", "editorEditable")
        SELECT 
            'ADMS Data' as "name",
            0 as "order",
            true as "visible", 
            true as "selectable",
            1.0 as "opacity",
            ms.id as "modelSetId",
            'ADMS_PARENT' as "importHash",
            false as "showForEdit",
            false as "blockApiUpdate",
            true as "editorVisible",
            true as "editorEditable"
        FROM pl_diagram."ModelSet" ms
        WHERE NOT EXISTS (
            SELECT 1 FROM pl_diagram."DispLayer" dl 
            WHERE dl."modelSetId" = ms.id AND dl."importHash" = 'ADMS_PARENT'
        );
    """
    )

    op.execute(
        """
        INSERT INTO pl_diagram."DispLayer" ("name", "order", "visible", "selectable", "opacity", "modelSetId", "importHash", "showForEdit", "blockApiUpdate", "editorVisible", "editorEditable")
        SELECT 
            'GIS/DXF Data' as "name",
            0 as "order",
            true as "visible",
            true as "selectable", 
            1.0 as "opacity",
            ms.id as "modelSetId",
            'GIS_DXF_PARENT' as "importHash",
            false as "showForEdit",
            false as "blockApiUpdate",
            true as "editorVisible",
            true as "editorEditable"
        FROM pl_diagram."ModelSet" ms
        WHERE NOT EXISTS (
            SELECT 1 FROM pl_diagram."DispLayer" dl 
            WHERE dl."modelSetId" = ms.id AND dl."importHash" = 'GIS_DXF_PARENT'
        );
    """
    )

    op.execute(
        """
        INSERT INTO pl_diagram."DispLayer" ("name", "order", "visible", "selectable", "opacity", "modelSetId", "importHash", "showForEdit", "blockApiUpdate", "editorVisible", "editorEditable")
        SELECT 
            'GeoJSON Data' as "name",
            0 as "order",
            true as "visible",
            true as "selectable", 
            1.0 as "opacity",
            ms.id as "modelSetId",
            'GEOJSON_PARENT' as "importHash",
            false as "showForEdit",
            false as "blockApiUpdate",
            true as "editorVisible",
            true as "editorEditable"
        FROM pl_diagram."ModelSet" ms
        WHERE NOT EXISTS (
            SELECT 1 FROM pl_diagram."DispLayer" dl 
            WHERE dl."modelSetId" = ms.id AND dl."importHash" = 'GEOJSON_PARENT'
        );
    """
    )

    # Update existing layers to assign them to appropriate parents
    # ADMS = "importHash" is an integer -> ADMS_PARENT
    op.execute(
        """
        UPDATE pl_diagram."DispLayer" 
        SET "parentId" = parent_layer.id
        FROM pl_diagram."DispLayer" parent_layer
        WHERE pl_diagram."DispLayer"."importHash" ~ '^[0-9]+$'
        AND pl_diagram."DispLayer"."importHash" NOT IN ('ADMS_PARENT', 'GEOJSON_PARENT', 'GIS_DXF_PARENT')
        AND parent_layer."importHash" = 'ADMS_PARENT'
        AND parent_layer."modelSetId" = pl_diagram."DispLayer"."modelSetId"
        AND parent_layer."parentId" is null;
    """
    )

    # GeoJSON = not ADMS, not GIS -> GEOJSON_PARENT
    op.execute(
        """
        UPDATE pl_diagram."DispLayer" 
        SET "parentId" = parent_layer.id
        FROM pl_diagram."DispLayer" parent_layer
        WHERE pl_diagram."DispLayer"."importHash" !~ '^[0-9]+$'
        AND (pl_diagram."DispLayer"."importHash" ilike '%osm%'
                OR pl_diagram."DispLayer"."importHash" ilike '%json%'
                OR pl_diagram."DispLayer"."importHash" ilike '%gsm%')
        AND pl_diagram."DispLayer"."importHash" NOT IN ('ADMS_PARENT', 'GEOJSON_PARENT', 'GIS_DXF_PARENT')
        AND parent_layer."importHash" = 'GEOJSON_PARENT'
        AND parent_layer."modelSetId" = pl_diagram."DispLayer"."modelSetId"
        AND pl_diagram."DispLayer"."parentId" is null;
    """
    )

    # GIS = not ADMS, and name = lower("importHash") -> GIS_DXF_PARENT
    op.execute(
        """
        UPDATE pl_diagram."DispLayer" 
        SET "parentId" = parent_layer.id
        FROM pl_diagram."DispLayer" parent_layer
        WHERE pl_diagram."DispLayer"."importHash" !~ '^[0-9]+$'
        AND NOT (pl_diagram."DispLayer"."importHash" ilike '%osm%'
                OR pl_diagram."DispLayer"."importHash" ilike '%json%'
                OR pl_diagram."DispLayer"."importHash" ilike '%gsm%')
        AND pl_diagram."DispLayer"."importHash" NOT IN ('ADMS_PARENT', 'GEOJSON_PARENT', 'GIS_DXF_PARENT')
        AND parent_layer."importHash" = 'GIS_DXF_PARENT'
        AND parent_layer."modelSetId" = pl_diagram."DispLayer"."modelSetId"
        AND pl_diagram."DispLayer"."parentId" is null;
    """
    )

    # GeoJSON = not ADMS, not GIS -> GEOJSON_PARENT
    op.execute(
        """
        UPDATE pl_diagram."DispLayer"
        SET "editorVisible" = null,
            "editorEditable" = null,
            "visible" = null,
            "selectable" = null
        WHERE pl_diagram."DispLayer"."parentId" in (
            SELECT id
            FROM pl_diagram."DispLayer"
            WHERE "importHash" IN (
                'GEOJSON_PARENT',
                'GIS_DXF_PARENT'
            )
        );
    """
    )


def downgrade():
    # Clear parentId assignments
    op.execute(
        """
        UPDATE pl_diagram."DispLayer" 
        SET "parentId" = NULL
        WHERE "parentId" IS NOT NULL;
    """
    )

    # Remove foreign key constraint
    op.drop_constraint(
        "fk_DispLayer_parentId", "DispLayer", schema="pl_diagram"
    )

    # Remove added columns
    op.drop_column("DispLayer", "parentId", schema="pl_diagram")
    op.drop_column("DispLayer", "editorVisible", schema="pl_diagram")
    op.drop_column("DispLayer", "editorEditable", schema="pl_diagram")

    # Make visible and selectable non-nullable again
    op.execute(
        """
        UPDATE pl_diagram."DispLayer" 
        SET "visible" = true 
        WHERE "visible" IS NULL;
    """
    )

    op.execute(
        """
        UPDATE pl_diagram."DispLayer" 
        SET "selectable" = false 
        WHERE "selectable" IS NULL;
    """
    )

    op.alter_column("DispLayer", "visible", nullable=False, schema="pl_diagram")
    op.alter_column(
        "DispLayer", "selectable", nullable=False, schema="pl_diagram"
    )

    # Remove parent layers
    op.execute(
        """
        DELETE FROM pl_diagram."DispLayer" 
        WHERE "importHash" IN ('ADMS_PARENT', 'GEOJSON_PARENT', 'GIS_DXF_PARENT');
    """
    )

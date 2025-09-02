from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndex
from peek_plugin_diagram._private.storage.ModelSet import (
    ModelCoordSetGridSizeTable,
)


gridSizeTable = ModelCoordSetGridSizeTable.__table__
gridKeyIndexTable = GridKeyIndex.__table__
dispBaseTable = DispBase.__table__

sql = (
    select(
        gridKeyIndexTable.c.gridKey,
        gridSizeTable.c.xGrid,
        gridSizeTable.c.yGrid,
    )
    .select_from(
        gridKeyIndexTable.join(
            dispBaseTable, dispBaseTable.c.id == gridKeyIndexTable.c.dispId
        ).join(
            gridSizeTable,
            gridSizeTable.c.coordSetId == gridKeyIndexTable.c.coordSetId,
        )
    )
    .where(dispBaseTable.c.key.in_([str(n) for n in range(100)]))
    .distinct()
)

print(
    str(
        sql.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )
)

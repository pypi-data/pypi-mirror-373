from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram.tuples.lookups.ImportDispColorTuple import (
    ImportDispColorTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispLayerTuple import (
    ImportDispLayerTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispLevelTuple import (
    ImportDispLevelTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispLineStyleTuple import (
    ImportDispLineStyleTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispTextStyleTuple import (
    ImportDispTextStyleTuple,
)

lookupTypeTableToImportTuple = {
    DispColorTable.LookupTypeE: ImportDispColorTuple.tupleType(),
    DispLayerTable.LookupTypeE: ImportDispLayerTuple.tupleType(),
    DispLevelTable.LookupTypeE: ImportDispLevelTuple.tupleType(),
    DispLineStyleTable.LookupTypeE: ImportDispLineStyleTuple.tupleType(),
    DispTextStyleTable.LookupTypeE: ImportDispTextStyleTuple.tupleType(),
}

lookupTypeImportTupleToTable = {
    v: k for k, v in lookupTypeTableToImportTuple.items()
}

lookupTypeTableEnumToTable = {
    DispColorTable.LookupTypeE: DispColorTable,
    DispLayerTable.LookupTypeE: DispLayerTable,
    DispLevelTable.LookupTypeE: DispLevelTable,
    DispLineStyleTable.LookupTypeE: DispLineStyleTable,
    DispTextStyleTable.LookupTypeE: DispTextStyleTable,
}

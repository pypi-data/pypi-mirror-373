
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable


@addTupleType
class ConfigLevelLookupDataLoaderTuple(TupleDataLoaderTupleABC):
    """ConfigLevelLookupDataLoaderTuple

    This tuple wraps the DispLevelTable object for loading and saving via the
    TupleDataLoader
    """
    __tupleType__ = diagramTuplePrefix + "ConfigLevelLookupDataLoaderTuple"

    item: DispLevelTable = TupleField()
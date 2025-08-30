
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable


@addTupleType
class ConfigLineStyleLookupDataLoaderTuple(TupleDataLoaderTupleABC):
    """ConfigLineStyleLookupDataLoaderTuple

    This tuple wraps the DispLineStyleTable object for loading and saving via the
    TupleDataLoader
    """
    __tupleType__ = diagramTuplePrefix + "ConfigLineStyleLookupDataLoaderTuple"

    item: DispLineStyleTable = TupleField()
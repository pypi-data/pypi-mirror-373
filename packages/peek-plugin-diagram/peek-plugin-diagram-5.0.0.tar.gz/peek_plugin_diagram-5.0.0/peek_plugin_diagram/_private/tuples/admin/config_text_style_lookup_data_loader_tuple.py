
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable


@addTupleType
class ConfigTextStyleLookupDataLoaderTuple(TupleDataLoaderTupleABC):
    """ConfigTextStyleLookupDataLoaderTuple

    This tuple wraps the DispTextStyleTable object for loading and saving via the
    TupleDataLoader
    """
    __tupleType__ = diagramTuplePrefix + "ConfigTextStyleLookupDataLoaderTuple"

    item: DispTextStyleTable = TupleField()
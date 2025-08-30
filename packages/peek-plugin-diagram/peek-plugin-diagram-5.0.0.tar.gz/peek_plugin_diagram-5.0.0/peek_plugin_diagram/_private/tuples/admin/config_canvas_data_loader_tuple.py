from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable


@addTupleType
class ConfigCanvasDataLoaderTuple(TupleDataLoaderTupleABC):
    __tupleType__ = diagramTuplePrefix + "ConfigCanvasDataLoaderTuple"

    item: ModelCoordSetTable = TupleField()

    modelSetKey: str = TupleField()
    coordSetKey: str = TupleField()

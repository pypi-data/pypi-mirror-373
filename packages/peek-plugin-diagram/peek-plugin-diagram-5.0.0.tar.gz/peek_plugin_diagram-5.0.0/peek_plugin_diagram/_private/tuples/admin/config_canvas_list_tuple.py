from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ConfigCanvasListTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ConfigCanvasListTuple"

    id: int = TupleField()
    key: str = TupleField()
    modelSetId: int = TupleField()
    modelSetKey: str = TupleField()
    name: str = TupleField()
    enabled: bool = TupleField()
    dispGroupTemplatesEnabled: bool = TupleField()
    edgeTemplatesEnabled: bool = TupleField()

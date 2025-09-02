from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.Tuple import Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class TriggerCanvasShapeCompileResultTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "TriggerCanvasShapeCompileResultTuple"

    shapesQueued: int = TupleField()
    gridsDeleted: int = TupleField()

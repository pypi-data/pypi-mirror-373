from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class TriggerCanvasShapeCompileTupleAction(TupleActionABC):
    __tupleType__ = diagramTuplePrefix + "TriggerCanvasShapeCompileTupleAction"

    canvasId: int = TupleField()

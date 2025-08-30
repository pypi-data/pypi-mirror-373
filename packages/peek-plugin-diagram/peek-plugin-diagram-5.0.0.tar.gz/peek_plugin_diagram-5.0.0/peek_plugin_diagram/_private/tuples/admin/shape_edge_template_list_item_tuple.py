from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ShapeEdgeTemplateListItemTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeEdgeListItemTuple"

    name: str = TupleField()

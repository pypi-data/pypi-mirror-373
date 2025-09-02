from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ShapeGroupListItemTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeGroupListItemTuple"

    name: str = TupleField()

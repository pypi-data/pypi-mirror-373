from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class PrivateDiagramLookupListTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "PrivateDiagramLookupListTuple"

    id: str = TupleField()
    key: str = TupleField()
    name: str = TupleField()

    data: dict = TupleField()

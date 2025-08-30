from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ConfigColorLookupListTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ConfigColorLookupListTuple"

    id: int = TupleField()
    modelSetId: int = TupleField()
    modelSetKey: str = TupleField()
    name: str = TupleField()
    importHash: str = TupleField()

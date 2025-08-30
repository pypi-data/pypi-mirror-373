from typing import List, Any

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ConfigModelSetListTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ConfigModelListTuple"

    id: int = TupleField()
    key: str = TupleField()
    name: str = TupleField()

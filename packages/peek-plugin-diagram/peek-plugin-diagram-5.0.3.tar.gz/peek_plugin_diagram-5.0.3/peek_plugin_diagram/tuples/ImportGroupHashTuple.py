from typing import Dict
from typing import List

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportGroupHashTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ImportGroupHashTuple"

    importGroupHash: List[str] = TupleField()

    def fromDict(self, d: Dict):
        importGroupHash = d.get("importGroupHash")
        if importGroupHash:
            self.importGroupHash = importGroupHash

from datetime import datetime
from typing import Dict

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)


@addTupleType
class GridUpdateDateTuple(Tuple, ACIUpdateDateTupleABC):
    __tupleType__ = diagramTuplePrefix + "GridUpdateDateTuple"

    # Improve performance of the JSON serialisation
    __rawJonableFields__ = ("updateDateByChunkKey",)

    initialLoadComplete: bool = TupleField()
    updateDateByChunkKey: Dict[str, str] = TupleField()

    @property
    def ckiUpdateDateByChunkKey(self):
        return self.updateDateByChunkKey

    def ckiSetUpdateDateByChunkKey(self, value: Dict[str, str]) -> None:
        self.updateDateByChunkKey = value

    @property
    def ckiInitialLoadComplete(self) -> bool:
        return self.initialLoadComplete

    def ckiSetInitialLoadComplete(self, value: bool) -> None:
        self.initialLoadComplete = value

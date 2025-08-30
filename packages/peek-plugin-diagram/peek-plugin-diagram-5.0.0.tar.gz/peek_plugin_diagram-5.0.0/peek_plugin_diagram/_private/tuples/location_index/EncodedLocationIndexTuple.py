from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)


@addTupleType
class EncodedLocationIndexTuple(Tuple, ACIEncodedChunkTupleABC):
    __tupleType__ = diagramTuplePrefix + "EncodedLocationIndexTuple"

    modelSetKey: str = TupleField()
    indexBucket: str = TupleField()

    # The LocationIndexTuple pre-encoded to a Payload
    encodedLocationIndexTuple: bytes = TupleField()
    lastUpdate: str = TupleField()

    @property
    def ckiChunkKey(self):
        return self.indexBucket

    @property
    def ckiEncodedData(self):
        return self.encodedLocationIndexTuple

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedLocationIndexTuple)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

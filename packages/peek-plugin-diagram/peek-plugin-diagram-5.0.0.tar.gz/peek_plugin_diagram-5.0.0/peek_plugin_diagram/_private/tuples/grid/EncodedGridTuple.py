from datetime import datetime

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)


@addTupleType
class EncodedGridTuple(Tuple, ACIEncodedChunkTupleABC):
    """Encoded Grid Tuple

    This tuple stores a pre-encoded version of a GridTuple

    """

    __tupleType__ = diagramTuplePrefix + "EncodedGridTuple"

    gridKey: str = TupleField()

    # A GridTuple, already encoded and ready for storage in the clients cache
    encodedGridTuple: str = TupleField()

    lastUpdate: datetime = TupleField()

    @property
    def ckiChunkKey(self):
        return self.gridKey

    @property
    def ckiEncodedData(self):
        return self.encodedGridTuple

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedGridTuple)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

import json
from datetime import datetime

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_diagram.tuples.grids.DecodedCompiledGridTuple import (
    DecodedCompiledGridTuple,
)


@addTupleType
class GridTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "GridTuple"

    gridKey: str = TupleField()
    dispJsonStr: str = TupleField()
    lastUpdate: datetime = TupleField()

    def toDecodedCompiledGridTuple(self) -> DecodedCompiledGridTuple:
        disps = json.loads(self.dispJsonStr)

        return DecodedCompiledGridTuple(
            gridKey=self.gridKey,
            shapes=disps,
            lastUpdate=self.lastUpdate,
            isLinkedWithLookups=False,
            compiledShapes=[],
        )

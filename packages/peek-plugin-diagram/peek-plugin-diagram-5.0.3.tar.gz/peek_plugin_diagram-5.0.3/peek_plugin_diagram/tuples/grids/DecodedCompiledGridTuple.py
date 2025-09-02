from datetime import datetime
from typing import List
from typing import Tuple


from vortex.Tuple import Tuple as VortexTuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class DecodedCompiledGridTuple(VortexTuple):
    __tupleType__ = diagramTuplePrefix + "DecodedCompiledGridTuple"

    gridKey: str = TupleField()
    shapes: List[dict] = TupleField()
    lastUpdate: datetime = TupleField()

    isLinkedWithLookups: bool = TupleField(defaultValue=False)
    compiledShapes: List[dict] = TupleField(defaultValue=[])

    @property
    def gridXY(self) -> Tuple[int, int]:
        _, _, xy = self.gridKey.partition(".")
        x, _, y = xy.partition("x")

        x = int(x)
        y = int(y)

        return x, y

from typing import Tuple

from vortex.Tuple import Tuple as VortexTuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class GridKeyTuple(VortexTuple):
    __tupleType__ = diagramTuplePrefix + "GridKeyTuple"

    gridKey: str = TupleField()

    width: float = TupleField()
    height: float = TupleField()

    shapeCount: int = TupleField()

    modelSetKey: str = TupleField()
    coordSetKey: str = TupleField()

    @property
    def gridXY(self) -> Tuple[int, int]:
        _, _, xy = self.gridKey.partition(".")
        x, _, y = xy.partition("x")

        x = int(x)
        y = int(y)

        return x, y

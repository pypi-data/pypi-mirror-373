from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.diagram_override.DiagramOverrideBase import (
    DiagramOverrideBase,
)
from peek_plugin_diagram.tuples.lookup_tuples.ShapeColorTuple import (
    ShapeColorTuple,
)


@addTupleType
class DiagramOverrideColor(DiagramOverrideBase):
    """Diagram Delta Color Override Tuple

    This delta applies an override colour to a set of display keys
    """

    __tupleType__ = diagramTuplePrefix + "DiagramOverrideColor"
    dispKeys_: list[str] = TupleField()
    lineColor_: ShapeColorTuple | None = TupleField()
    fillColor_: ShapeColorTuple | None = TupleField()
    color_: ShapeColorTuple | None = TupleField()

    @property
    def dispKeys(self) -> list[str]:
        return self.dispKeys_

    @property
    def lineColor(self) -> ShapeColorTuple | None:
        return self.lineColor_

    @property
    def fillColor(self) -> ShapeColorTuple | None:
        return self.fillColor_

    @property
    def color(self) -> ShapeColorTuple | None:
        return self.color_

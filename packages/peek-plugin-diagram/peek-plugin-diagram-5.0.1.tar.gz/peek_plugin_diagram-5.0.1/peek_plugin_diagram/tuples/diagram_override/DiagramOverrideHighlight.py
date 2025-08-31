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
class DiagramOverrideHighlight(DiagramOverrideBase):
    """Diagram Delta Color Override Tuple

    This delta applies an override colour to a set of display keys
    """

    __tupleType__ = diagramTuplePrefix + "DiagramOverrideHighlight"
    dispKeys_: list[str] = TupleField()
    color_: ShapeColorTuple = TupleField()

    @property
    def dispKeys(self) -> list[str]:
        return self.dispKeys_

    @property
    def color(self) -> ShapeColorTuple:
        return self.color_

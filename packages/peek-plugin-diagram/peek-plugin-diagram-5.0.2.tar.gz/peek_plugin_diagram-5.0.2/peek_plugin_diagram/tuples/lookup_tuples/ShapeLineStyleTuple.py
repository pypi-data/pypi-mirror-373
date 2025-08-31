import json

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ShapeLineStyleTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeLineStyleTuple"

    #: Misc data holder
    data = TupleField()

    #: Key field used to abstract ID for APIs with other plugins
    key = TupleField()

    name: str = TupleField()
    backgroundFillDashSpace: bool = TupleField()
    capStyle: str = TupleField()
    joinStyle: str = TupleField()
    dashPattern: str = TupleField()
    startArrowSize: int = TupleField()
    endArrowSize: int = TupleField()
    winStyle: int = TupleField()

    modelSetKey: str = TupleField()

    importHash: str = TupleField()
    scalable: bool = TupleField()

    showForEdit: bool = TupleField()
    blockApiUpdate: bool = TupleField()

    @property
    def dashPatternParsed(self):
        if self.dashPattern is None:
            return None
        return json.loads(self.dashPattern)

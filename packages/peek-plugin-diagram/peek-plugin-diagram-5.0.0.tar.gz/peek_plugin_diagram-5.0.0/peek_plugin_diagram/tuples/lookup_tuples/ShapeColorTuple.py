from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.ColorUtil import invertColor


@addTupleType
class ShapeColorTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeColorTuple"

    #: Misc data holder
    data = TupleField()

    #: Key field used to abstract ID for APIs with other plugins
    key = TupleField()

    name: str = TupleField()

    darkColor: str = TupleField()
    lightColor: str = TupleField()
    darkFillBase64Image: str = TupleField()
    lightFillBase64Image: str = TupleField()

    altColor: str = TupleField()
    swapPeriod: float = TupleField()

    modelSetKey: str = TupleField()

    importHash: str = TupleField()

    showForEdit: bool = TupleField()

    blockApiUpdate: bool = TupleField()

    def getColor(self, isLightMode: bool) -> str:
        return self.lightColor if isLightMode else self.darkColor

    @property
    def color(self):
        return self.darkColor

    @color.setter
    def color(self, value: str):
        self.darkColor = value
        if value:
            self.lightColor = invertColor(value, "#fff")

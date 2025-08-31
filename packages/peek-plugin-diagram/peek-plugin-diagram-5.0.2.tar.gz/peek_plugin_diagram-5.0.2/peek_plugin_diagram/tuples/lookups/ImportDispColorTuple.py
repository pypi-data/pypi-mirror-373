from typing import Optional

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.ColorUtil import invertColor


@addTupleType
class ImportDispColorTuple(Tuple):
    """Imported Display Color

    This tuple is used by other plugins to load colours into the diagram.

    """

    __tupleType__ = diagramTuplePrefix + "ImportDispColorTuple"

    #:  The name of the color
    name: str = TupleField()

    #:  The color
    darkColor: str = TupleField()
    lightColor: str = TupleField()

    darkFillBase64Image: Optional[str] = TupleField()
    lightFillBase64Image: Optional[str] = TupleField()

    #:  The alt color
    altColor: Optional[str] = TupleField()

    #:  The swap period if this is a flashing colour
    swapPeriod: Optional[float] = TupleField()

    #:  The name of the model set for this colour
    modelSetKey: str = TupleField()

    #:  The import hash for this colour
    importHash: str = TupleField()

    showForEdit: bool = TupleField(defaultValue=False)

    blockApiUpdate: bool = TupleField(defaultValue=False)

    @property
    def color(self):
        return self.darkColor

    @color.setter
    def color(self, value: str):
        self.darkColor = value
        if value:
            self.lightColor = invertColor(value, "#fff")

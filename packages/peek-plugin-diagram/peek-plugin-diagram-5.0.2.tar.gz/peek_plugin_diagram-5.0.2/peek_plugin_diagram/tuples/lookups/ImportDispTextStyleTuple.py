from typing import Optional

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportDispTextStyleTuple(Tuple):
    """Import Display Text Style Tuple"""

    __tupleType__ = diagramTuplePrefix + "ImportDispTextStyleTuple"

    name: str = TupleField()

    fontName: str = TupleField()
    fontSize: float = TupleField()

    STYLE_BOLD = "bold"
    fontStyle: str = TupleField()

    scalable: bool = TupleField(defaultValue=True)
    scaleFactor: float = TupleField(defaultValue=1)

    importHash: str = TupleField()

    modelSetKey: str = TupleField()

    #: a parameter to put white space between text repeats along a
    # path in 'ImportDispCurvedTextTuple.geom'.
    #  'spacingBetweenTexts' is in range of (0, +∞)
    #  The spacing is the spacing distance at zoom level 1, in the coordinate
    #  system unit.
    spacingBetweenTexts: float = TupleField(defaultValue=100)

    borderWidth: Optional[float] = TupleField()

    showForEdit: bool = TupleField(defaultValue=False)

    blockApiUpdate: bool = TupleField(defaultValue=False)

    wrapTextAtChars: int = TupleField(defaultValue=None)

    wrapTextAtCharSplitBetweenWords: bool = TupleField(defaultValue=True)

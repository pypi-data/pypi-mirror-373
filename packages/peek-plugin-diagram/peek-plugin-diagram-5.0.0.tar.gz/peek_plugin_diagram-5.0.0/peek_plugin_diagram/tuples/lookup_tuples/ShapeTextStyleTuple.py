from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ShapeTextStyleTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeTextStyleTuple"

    #: Misc data holder
    data = TupleField()

    #: Key field used to abstract ID for APIs with other plugins
    key = TupleField()

    name: str = TupleField()
    fontName: str = TupleField()
    fontSize: int = TupleField()
    fontStyle: str = TupleField()
    scalable: bool = TupleField()
    scaleFactor: float = TupleField()
    spacingBetweenTexts: float = TupleField()

    modelSetKey: str = TupleField()

    importHash: str = TupleField()

    borderWidth: float = TupleField()

    showForEdit: bool = TupleField()

    blockApiUpdate: bool = TupleField()

    wrapTextAtChars: int = TupleField()

    wrapTextAtCharSplitBetweenWords: bool = TupleField()

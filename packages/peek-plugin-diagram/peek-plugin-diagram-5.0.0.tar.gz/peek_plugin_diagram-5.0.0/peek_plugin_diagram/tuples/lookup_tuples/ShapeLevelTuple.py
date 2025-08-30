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
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ShapeLevelTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeLevelTuple"

    #: Misc data holder
    data = TupleField()

    #: Key field used to abstract ID for APIs with other plugins
    key = TupleField()

    name: str = TupleField()
    order: int = TupleField()
    minZoom: float = TupleField()
    maxZoom: float = TupleField()

    modelSetKey: str = TupleField()
    coordSetKey: str = TupleField()

    importHash: str = TupleField()

    showForEdit: bool = TupleField()

    blockApiUpdate: bool = TupleField()

    def isVisibleAtZoom(self, zoom: float) -> bool:
        return self.minZoom <= zoom < self.maxZoom

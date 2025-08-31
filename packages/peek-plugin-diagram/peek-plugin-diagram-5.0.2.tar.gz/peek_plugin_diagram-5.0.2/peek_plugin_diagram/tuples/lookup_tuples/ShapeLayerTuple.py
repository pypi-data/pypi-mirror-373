from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ShapeLayerTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "ShapeLayerTuple"

    #: Misc data holder
    data = TupleField()

    #: Key field used to abstract ID for APIs with other plugins
    key = TupleField()
    parentKey: str = TupleField(defaultValue=None)

    name: str = TupleField()
    order: int = TupleField()
    selectable: bool = TupleField(defaultValue=None)
    visible: bool = TupleField(defaultValue=None)
    editorVisible: bool = TupleField(defaultValue=True)
    editorEditable: bool = TupleField(defaultValue=True)
    opacity: float = TupleField()

    modelSetKey: str = TupleField()

    importHash: str = TupleField()

    showForEdit: bool = TupleField()

    blockApiUpdate: bool = TupleField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parent/Child relationships - underscore prevents serialization
        self._parentLayer = None
        self._childLayers = []

    @property
    def parentLayer(self):
        return self._parentLayer

    @parentLayer.setter
    def parentLayer(self, value):
        self._parentLayer = value

    @property
    def childLayers(self):
        return self._childLayers

    @childLayers.setter
    def childLayers(self, value):
        self._childLayers = value

    def isVisibleAtZoom(self, zoom: float) -> bool:
        return self.minZoom <= zoom < self.maxZoom

    def calculateEffectiveVisibility(self) -> bool:
        if self.visible is not None:
            return self.visible

        if self._parentLayer:
            return self._parentLayer.calculateEffectiveVisibility()

        return True

    def calculateEffectiveEditorVisibility(self) -> bool:
        if self.editorVisible is not None:
            return self.editorVisible

        if self._parentLayer:
            return self._parentLayer.calculateEffectiveEditorVisibility()

        return True

    def calculateEffectiveSelectability(self) -> bool:
        if self.selectable is not None:
            return self.selectable

        if self._parentLayer:
            return self._parentLayer.calculateEffectiveSelectability()

        return True

    def calculateEffectiveEditorEditable(self) -> bool:
        if self.editorEditable is not None:
            return self.editorEditable

        if self._parentLayer:
            return self._parentLayer.calculateEffectiveEditorEditable()

        return True
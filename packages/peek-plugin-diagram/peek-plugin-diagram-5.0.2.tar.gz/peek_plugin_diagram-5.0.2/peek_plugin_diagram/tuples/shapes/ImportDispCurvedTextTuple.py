from typing import Optional, List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import (
    ImportLiveDbDispLinkTuple,
)
from peek_plugin_diagram.tuples.shapes.ImportDispPolylineTuple import (
    ImportDispPolylineTuple,
)


@addTupleType
class ImportDispCurvedTextTuple(Tuple):
    """Imported Display Curved Text

    This tuple is used by other plugins to load curved TEXT objects into the
    diagram.
    """

    __tupleType__ = diagramTuplePrefix + "ImportDispCurvedTextTuple"

    ### BEGIN DISP COMMON FIELDS ###

    # The actions to perform when this line is clicked
    ACTION_NONE = ImportDispPolylineTuple.ACTION_NONE
    ACTION_POSITION_ON = ImportDispPolylineTuple.ACTION_POSITION_ON
    # For ACTION_POSITION_ON, Add the following to the display data
    # data['actionPos'] = {k='coordSetKey', x=x, y=y, z=zoom}

    #: Key, This value is a unique ID of the object that this graphic represents
    # It's used to link this graphical object to objects in other plugins, like vertices
    # in the peek-plugin-graphdb plugin.
    # Length = 50
    key: Optional[str] = TupleField()

    #: Selectable, Is this item selectable?, the layer also needs selectable=true
    selectable: Optional[bool] = TupleField()

    #: Overlay, Is this shape an overlay?, Overlays are sometimes used to add dynamic
    # data to the diagram, such as a Job, Operation, or placing a green box over a red
    # one to change it's state.
    overlay: Optional[bool] = TupleField()

    #: Action, An action to perform when this display item is clicked.
    # See the ACTION_NONE constants for values.
    action: Optional[int] = TupleField(None)

    #: Data, Generic data, this is passed to the popup context in the UI.
    # peek_plugin_diagram doesn't care as long as it's json compatible or None
    # Json Length = 400
    data: Optional[dict] = TupleField(None)

    #: The hash of the level to link to (Matches ImportDispLevel.importHash)
    levelHash: str = TupleField()

    #: The hash of the layer to link to (Matches ImportDispLayer.importHash)
    layerHash: str = TupleField()

    #: The unique hash of this display object
    importHash: str = TupleField()

    #: The Z Order of this display object when compared against other objects on
    # same layer and level.
    zOrder: int = TupleField()

    #: The unique hash for all the display items imported in a group with this one.
    #: for example, a page or tile reference.
    importGroupHash: str = TupleField()

    #: The key of the ModelSet to import into
    modelSetKey: str = TupleField()

    #: The Key of the Coordinate Set to import into
    coordSetKey: str = TupleField()

    #: Related links to LiveDB values for this display item
    liveDbDispLinks: List[ImportLiveDbDispLinkTuple] = TupleField([])

    #: Parent DispGroup Hash, If this disp is part of a disp group then set this field to
    # the ImportDispGroupTuple.importHash fields value
    # NOTE: If this disp is part of a display group, then the GEOM coordinates need to
    # be relative to 0x0.
    # NOTE: Disps that are a part of a group must all be imported with the same
    # importGroupHash, during the same import call.
    parentDispGroupHash: str = TupleField()

    ### BEGIN FIELDS FOR THIS DISP ###

    textStyleHash: str = TupleField()
    colorHash: Optional[str] = TupleField()
    borderColorHash: Optional[str] = TupleField()

    # the hidden path where the text places on.
    geom: List[List[float]] = TupleField()

    #: The value of the text
    text: str = TupleField()

    #: This field stores text with format strings that are used to create the text above.
    textFormat: Optional[str] = TupleField()

    #: a parameter to put white space between text repeats along a
    # path in 'ImportDispCurvedTextTuple.geom'.
    #  'spacingBetweenTexts' is in range of (0, +∞)
    #  The spacing is the distance at zoom level 1, in the coordinate
    #  system unit. The actual distance at a certain zoom level will be scaled
    #  from this length.
    spacingBetweenTexts: float = TupleField(defaultValue=100)

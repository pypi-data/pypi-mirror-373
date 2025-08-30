"""
 * orm.Display.py
 *
 *  Copyright Synerty Pty Ltd 2011
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""

import typing

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from sqlalchemy import Column, orm, BigInteger, SmallInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import reconstructor
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.sqltypes import Float, DateTime
from vortex.Tuple import Tuple, addTupleType, TupleField, JSON_EXCLUDE

from .DeclarativeBase import DeclarativeBase
from .Lookups import DispColorTable
from .Lookups import DispLayerTable
from .Lookups import DispLevelTable
from .Lookups import DispLineStyleTable
from .Lookups import DispTextStyleTable
from .ModelSet import ModelCoordSetTable
from .branch.BranchIndex import BranchIndex

DISP_SHORT_ATTR_NAME_MAP = {
    "colorId": "c",
    "fillColorId": "fc",
    "borderColorId": "bc",
    "lineColorId": "lc",
    "lineStyleId": "ls",
    "lineWidth": "w",
    "text": "te",
    "groupId": "gi",
    "targetGroupId": "tg",
}


class DispBase(DeclarativeBase, Tuple):
    __tablename__ = "DispBase"

    # Types
    # Must align with constants in javascript DispBase class
    GROUP = 10
    GROUP_PTR = 11
    TEXT = 40
    POLYGON = 50
    POLYLINE = 51
    EDGE_TEMPLATE = 52
    ELLIPSE = 60
    NULL = 70
    CURVED_TEXT = 80

    ACTION_NONE = None
    ACTION_POSITION_ON = 1

    id = Column(BigInteger, primary_key=True)

    type = Column(Integer, doc=JSON_EXCLUDE, nullable=False)

    # ===== START BRANCH

    #: The branch that this Disp belongs to.
    branchId = Column(
        BigInteger, ForeignKey(BranchIndex.id, ondelete="CASCADE"), doc="bi"
    )

    #: The stage of the branch that this DISP
    branchStage = Column(Integer, doc="bs")

    #: This is the unique hash of the contents of this disp within this coordSetId.
    hashId = Column(String, doc="hid")

    #: The coordSetId+hashId that this disp replaces (for branches)
    # ForeignKey('DispBase.id', ondelete='SET NULL'),
    replacesHashId = Column(String, doc="rid")

    # ===== END BRANCH

    #: Used for disps that belong to a DispGroup
    groupId = Column(
        BigInteger, ForeignKey("DispBase.id", ondelete="CASCADE"), doc="gi"
    )

    coordSetId = Column(
        Integer,
        ForeignKey("ModelCoordSet.id", ondelete="CASCADE"),
        doc=JSON_EXCLUDE,
        nullable=False,
    )
    coordSet = relationship(ModelCoordSetTable)

    #: Layer
    layerId = Column(Integer, ForeignKey("DispLayer.id"), doc="la")
    layer = relationship(DispLayerTable)

    #: Layer
    levelId = Column(Integer, ForeignKey("DispLevel.id"), doc="le")
    level = relationship(DispLevelTable)

    #: Order
    zOrder = Column(Integer, server_default="0", nullable=False, doc="z")

    # MAX_STR
    dispJson = Column(String, doc=JSON_EXCLUDE)

    #: The location of this Disp EG - [coordSetId, dispId, 0.0, 0.0] = [..., x, y]
    locationJson = Column(String, doc=JSON_EXCLUDE)

    #: Key, This value is a unique ID of the object that this graphic represents
    key = Column(String, doc="k")

    #: Selectable, Is is this item selectable?, the layer also needs selectable=true
    selectable = Column(
        Boolean, doc="s", nullable=False, server_default="false"
    )

    #: Overlay, Is is this item an overlay?, Overlays are sometimes used to add dynamic
    # data to the diagram, such as a Job, Operation, or placing a green box over a red
    # one to change it's state.
    overlay = Column(Boolean, doc="o", nullable=False, server_default="false")

    #: Action, This determines what happens when a user clicks on this shape.
    action = Column(SmallInteger, doc="a")

    #: Data, Generic data that is passed in the context for the item select popup
    dataJson = Column(String, doc="d")

    # THIS FIELD IS NOT USED ANYWHERE!!!!
    importUpdateDate = Column(DateTime(True), doc=JSON_EXCLUDE)

    importHash = Column(String, doc=JSON_EXCLUDE)
    importGroupHash = Column(String, doc=JSON_EXCLUDE)

    __mapper_args__ = {"polymorphic_on": type, "with_polymorphic": "*"}

    __table_args__: typing.Tuple = (
        Index("idx_Disp_importGroupHash", importGroupHash, unique=False),
        # Index("idx_Disp_importHash", importHash, unique=True),
        Index("idx_Disp_importUpdateDate", importUpdateDate, unique=False),
        Index("idx_Disp_layerId", layerId, unique=False),
        Index("idx_Disp_levelId", levelId, unique=False),
        Index("idx_Disp_coordSetId_", coordSetId, unique=False),
        Index("idx_Disp_groupId", groupId, unique=False),
        Index("idx_Disp_branchId", branchId, unique=False),
        # We need this for the diagram API method getGridKeysFromShapeKeys
        Index("idx_Disp_key", key, unique=False),
        # Index("idx_Disp_hashId", coordSetId, hashId, unique=True),
        # Index("idx_Disp_replacesHashId", replacesHashId),
    )


@addTupleType
class DispNull(DispBase):
    """Disp Null

    This display type does not display at all, It's an object that marks the deletion
    of a prior Disp by a branch.

    Disps in branches replace existing disps, thats how the store the change.
    This disp replaces an existing disp with nothing, with the effect of deleting it.

    This disp does have a geometry, which is equivilent to the bounding box of the shape
    it replaces.

    This whole approach allows the branch delete mechanism to slot into the existing
    diagram structures.

    """

    __tablename__ = "DispNull"
    __tupleTypeShort__ = "DN"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.NULL

    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    geomJson = Column(String, nullable=False, doc="g")

    __table_args__: typing.Tuple = ()

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispText(DispBase):
    __tablename__ = "DispText"
    __tupleTypeShort__ = "DT"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.TEXT

    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    verticalAlign = Column(
        Integer, doc="va", nullable=False, server_default="-1"
    )
    horizontalAlign = Column(
        Integer, doc="ha", nullable=False, server_default="0"
    )
    rotation = Column(Float, doc="r", nullable=False, server_default="0")
    text = Column(
        String, doc="te", nullable=True, server_default="new text label"
    )
    textFormat = Column(String(1000), doc=JSON_EXCLUDE, nullable=True)

    textHeight = Column(Float, doc="th", nullable=True)
    textHStretch = Column(Float, doc="hs", nullable=False, server_default="1")

    geomJson = Column(String, nullable=False, doc="g")

    colorId = Column(Integer, ForeignKey("DispColor.id"), doc="c")
    color = relationship(DispColorTable, foreign_keys=[colorId])

    borderColorId = Column(Integer, ForeignKey("DispColor.id"), doc="bc")
    borderColor = relationship(DispColorTable, foreign_keys=[borderColorId])

    textStyleId = Column(
        Integer, ForeignKey("DispTextStyle.id"), doc="fs", nullable=False
    )
    textStyle = relationship(DispTextStyleTable)

    __table_args__: typing.Tuple = (
        # Commented out, we don't delete lookups during normal operation
        # and keeping this index maintained costs time
        # Index("idx_DispText_colorId", colorId, unique=False),
        # Index("idx_DispText_styleId", textStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispCurvedText(DispBase):
    __tablename__ = "DispCurvedText"
    __tupleTypeShort__ = "DCT"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.CURVED_TEXT

    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    text = Column(
        String, doc="te", nullable=True, server_default="new text label"
    )

    geomJson = Column(String, nullable=False, doc="g")

    colorId = Column(Integer, ForeignKey("DispColor.id"), doc="c")
    color = relationship(DispColorTable, foreign_keys=[colorId])

    textStyleId = Column(
        Integer, ForeignKey("DispTextStyle.id"), doc="fs", nullable=False
    )
    textStyle = relationship(DispTextStyleTable)
    spacingBetweenTexts = Column(
        Float, doc="sbt", nullable=True, server_default="100"
    )
    borderColorId = Column(Integer, ForeignKey("DispColor.id"), doc="bc")
    borderColor = relationship(DispColorTable, foreign_keys=[borderColorId])

    __table_args__: typing.Tuple = (
        # Commented out, we don't delete lookups during normal operation
        # and keeping this index maintained costs time
        # Index("idx_DispText_colorId", colorId, unique=False),
        # Index("idx_DispText_styleId", textStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispPolygon(DispBase):
    __tablename__ = "DispPolygon"
    __tupleTypeShort__ = "DPG"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.POLYGON
    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    cornerRadius = Column(Float, doc="cr", nullable=False, server_default="0")
    lineWidth = Column(Integer, doc="w", nullable=False, server_default="2")

    geomJson = Column(String, nullable=False, doc="g")

    fillColorId = Column(Integer, ForeignKey("DispColor.id"), doc="fc")
    fillColor = relationship(DispColorTable, foreign_keys=fillColorId)

    FILL_TOP_TO_BOTTOM = 0
    FILL_BOTTOM_TO_TOP = 1
    FILL_RIGHT_TO_LEFT = 2
    FILL_LEFT_TO_RIGHT = 3
    fillDirection = Column(Integer, doc="fd")
    fillPercent = Column(Float, doc="fp")
    isRectangle = Column(Boolean, doc="r")

    lineColorId = Column(Integer, ForeignKey("DispColor.id"), doc="lc")
    lineColor = relationship(DispColorTable, foreign_keys=lineColorId)

    lineStyleId = Column(Integer, ForeignKey("DispLineStyle.id"), doc="ls")
    lineStyle = relationship(DispLineStyleTable)

    __table_args__ = (
        # Commented out, we don't delete lookups during normal operation
        # and keeping this index maintained costs time
        # Index("idx_DispPolygon_fillColorId", fillColorId, unique=False),
        # Index("idx_DispPolygon_lineColorId", lineColorId, unique=False),
        # Index("idx_DispPolygon_lineStyleId", lineStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispPolyline(DispBase):
    __tablename__ = "DispPolyline"
    __tupleTypeShort__ = "DPL"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.POLYLINE
    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    lineWidth = Column(Integer, doc="w", nullable=False, server_default="2")

    geomJson = Column(String, nullable=False, doc="g")

    lineColorId = Column(Integer, ForeignKey("DispColor.id"), doc="lc")
    lineColor = relationship(DispColorTable, foreign_keys=lineColorId)

    borderWidth = Column(Integer, doc="bw", nullable=True)
    borderColorId = Column(Integer, ForeignKey("DispColor.id"), doc="bc")
    borderColor = relationship(DispColorTable, foreign_keys=borderColorId)

    lineStyleId = Column(Integer, ForeignKey("DispLineStyle.id"), doc="ls")
    lineStyle = relationship(DispLineStyleTable)

    #: EdgeColor
    # This is an alternate line color.
    edgeColorId = Column(
        Integer,
        ForeignKey("DispColor.id", name="DispGroupPointer_edgeColorId_fkey"),
        doc="ec",
    )

    #: Start Key, The key of another disp object,
    # If the start point of this graphic is linked another disp obj
    startKey = Column(String(50), doc="sk")

    #: End Key, The key of another disp object,
    # If the end point of this graphic is linked another disp obj
    endKey = Column(String(50), doc="ek")

    #: Start end type, is this an arrow, etc?
    startEndType = Column(Integer, doc="st")

    #: End End Type, See Start end type
    endEndType = Column(Integer, doc="et")

    targetEdgeTemplateId = Column(
        Integer,
        ForeignKey("DispEdgeTemplate.id", ondelete="SET NULL"),
        doc="ti",
    )

    targetEdgeTemplateName = Column(String, doc="tn")

    __table_args__ = (
        # Commented out, we don't delete lookups during normal operation
        # and keeping this index maintained costs time
        # Index("idx_DispPolyline_lineColorId", lineColorId, unique=False),
        # Index("idx_DispPolyline_lineStyleId", lineStyleId, unique=False),
        # Index("idx_DispPolyline_edgeColorId", lineColorId, unique=False),
        Index("idx_DispPolyline_startKey", startKey, unique=False),
        Index("idx_DispPolyline_endKey", endKey, unique=False),
        Index(
            "idx_DispPolyline_targetEdgeTemplateId",
            targetEdgeTemplateId,
            unique=False,
        ),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispEllipse(DispBase):
    __tablename__ = "DispEllipse"
    __tupleTypeShort__ = "DE"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.ELLIPSE
    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    xRadius = Column(Float, doc="xr", nullable=False, server_default="10.0")
    yRadius = Column(Float, doc="yr", nullable=False, server_default="10.0")
    rotation = Column(Float, doc="r", nullable=False, server_default="0")
    startAngle = Column(Float, doc="sa", nullable=False, server_default="0")
    endAngle = Column(Float, doc="ea", nullable=False, server_default="360")
    lineWidth = Column(Integer, doc="w", nullable=False, server_default="2")

    geomJson = Column(String, nullable=False, doc="g")

    fillColorId = Column(Integer, ForeignKey("DispColor.id"), doc="fc")
    fillColor = relationship(DispColorTable, foreign_keys=fillColorId)

    lineColorId = Column(Integer, ForeignKey("DispColor.id"), doc="lc")
    lineColor = relationship(DispColorTable, foreign_keys=lineColorId)

    lineStyleId = Column(Integer, ForeignKey("DispLineStyle.id"), doc="ls")
    lineStyle = relationship(DispLineStyleTable)

    __table_args__ = (
        # Commented out, we don't delete lookups during normal operation
        # and keeping this index maintained costs time
        # Index("idx_DispEllipse_fillColorId", fillColorId, unique=False),
        # Index("idx_DispEllipse_lineColorId", lineColorId, unique=False),
        # Index("idx_DispEllipse_lineStyleId", lineStyleId, unique=False),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispGroup(DispBase):
    """Disp Group

    This object is used to store a template group of disps. These are used for placing
    or updating existing disps in a DispGroupPtr

    """

    __tablename__ = "DispGroup"
    __tupleTypeShort__ = "DG"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.GROUP
    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    # TODO: this needs to be unique WITH the coordSetId
    name = Column(String, doc="n", nullable=False)
    compileAsTemplate = Column(
        Boolean, doc=JSON_EXCLUDE, nullable=False, server_default="false"
    )

    disps = relationship(
        DispBase,
        primaryjoin="DispBase.groupId==DispGroup.id",
        foreign_keys=[DispBase.groupId],
        remote_side="DispBase.groupId",
    )

    #: This field stores an array of disps that belong to this group.
    dispsForJson = TupleField(shortName="di")

    @reconstructor
    def __init__(self):
        DispBase.__init__(self)


@addTupleType
class DispEdgeTemplate(DispBase):
    """Disp Line Template

    This object is used to create new lines in the diagram that also represent
     edges in the GraphDB model.

    At this stage it's just a template for a new line type.

    """

    __tablename__ = "DispEdgeTemplate"
    __tupleTypeShort__ = "DLT"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.EDGE_TEMPLATE
    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    name = Column(String, doc="n", nullable=False)

    lineWidth = Column(Integer, doc="w", nullable=False, server_default="2")

    lineColorId = Column(Integer, ForeignKey("DispColor.id"), doc="lc")
    lineColor = relationship(DispColorTable, foreign_keys=lineColorId)

    lineStyleId = Column(Integer, ForeignKey("DispLineStyle.id"), doc="ls")
    lineStyle = relationship(DispLineStyleTable)

    #: Start end type, is this an arrow, etc?
    startEndType = Column(Integer, doc="st")

    #: End End Type, See Start end type
    endEndType = Column(Integer, doc="et")

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass


@addTupleType
class DispGroupPointer(DispBase):
    __tablename__ = "DispGroupPointer"
    __tupleTypeShort__ = "DGP"
    __tupleType__ = diagramTuplePrefix + __tablename__

    RENDERABLE_TYPE = DispBase.GROUP_PTR
    __mapper_args__ = {"polymorphic_identity": RENDERABLE_TYPE}

    id = Column(
        BigInteger,
        ForeignKey("DispBase.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )

    rotation = Column(Integer, doc="r", server_default="0", nullable=False)

    verticalScale = Column(
        Float, doc="vs", nullable=False, server_default="1.0"
    )
    horizontalScale = Column(
        Float, doc="hs", nullable=False, server_default="1.0"
    )

    geomJson = Column(String, nullable=False, doc="g")

    targetDispGroupId = Column(
        BigInteger, ForeignKey("DispGroup.id", ondelete="SET NULL"), doc="tg"
    )

    targetDispGroupName = Column(String, doc="tn")

    disps = relationship(
        DispBase,
        primaryjoin="DispBase.groupId==DispGroupPointer.id",
        foreign_keys=[DispBase.groupId],
        remote_side="DispBase.groupId",
    )

    __table_args__ = (
        Index(
            "idxDispGroupPointer_targetDispGroupId",
            targetDispGroupId,
            unique=False,
        ),
    )

    # noinspection PyMissingConstructor
    @orm.reconstructor
    def __init__(self):
        pass

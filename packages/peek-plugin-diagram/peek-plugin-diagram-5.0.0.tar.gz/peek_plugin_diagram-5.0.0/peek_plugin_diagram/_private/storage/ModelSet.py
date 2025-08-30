"""
 * orm.ModelSet.py
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

import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.types import Float
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.DiagramCoordSetTuple import (
    DiagramCoordSetTuple,
)
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class ModelSetTable(DeclarativeBase, Tuple):
    __tablename__ = "ModelSet"
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    comment = Column(String)

    coordSets = relationship(
        "ModelCoordSetTable",
        remote_side="ModelCoordSetTable.modelSetId",
        primaryjoin="ModelSetTable.id==ModelCoordSetTable.modelSetId",
        viewonly=True,
    )

    __table_args__ = (Index("idx_ModelSet_name", name, unique=True),)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)


@addTupleType
class ModelCoordSetTable(DeclarativeBase, Tuple):
    """Coordinate Sets"""

    __tablename__ = "ModelCoordSet"
    __tupleType__ = diagramTuplePrefix + __tablename__

    # Ensure gridSizes is serialised when it's sent to the client
    __fieldNames__ = ["gridSizes"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    initialPanX = Column(Float, nullable=False, server_default="0")
    initialPanY = Column(Float, nullable=False, server_default="0")
    initialZoom = Column(Float, nullable=False, server_default="2.0")
    initialDarkMode = Column(Boolean, nullable=False, server_default="true")
    positionOnZoom = Column(Float, nullable=False, server_default="2.0")

    backgroundDarkColor = Column(
        String, nullable=False, server_default="#ffffff"
    )
    backgroundLightColor = Column(
        String, nullable=False, server_default="#ffffff"
    )

    enabled = Column(Boolean, nullable=False, server_default="false")
    lightModeEnabled = Column(Boolean, nullable=False, server_default="true")

    modelSetId = Column(
        Integer, ForeignKey("ModelSet.id", ondelete="CASCADE"), nullable=False
    )
    modelSet = relationship(
        ModelSetTable,
        foreign_keys=[modelSetId],
        primaryjoin="ModelSetTable.id==ModelCoordSetTable.modelSetId",
        overlaps="coordSets",
        viewonly=True,
    )

    # Grid size settings
    gridSizes = relationship(
        "ModelCoordSetGridSizeTable",
        lazy="subquery",
        order_by="ModelCoordSetGridSizeTable.key",
        overlaps="coordSet",
        viewonly=True,
        primaryjoin="ModelCoordSetTable.id==ModelCoordSetGridSizeTable.coordSetId",
    )

    minZoom = Column(Float, nullable=False, server_default="0.01")
    maxZoom = Column(Float, nullable=False, server_default="10.0")

    multiplierX = Column(Float, nullable=False, server_default="1")
    multiplierY = Column(Float, nullable=False, server_default="1")

    offsetX = Column(Float, nullable=False, server_default="0")
    offsetY = Column(Float, nullable=False, server_default="0")

    comment = Column(String)

    importId1 = Column(Integer)
    importId2 = Column(String(100))

    #: Misc data holder
    data = TupleField()

    #: Show this Coord Set as a group of DispGroups to choose from in the Editor
    dispGroupTemplatesEnabled = Column(
        Boolean, nullable=False, server_default="false"
    )

    #: Show this Coord Set as a group of Line Templates to choose from in the Editor
    edgeTemplatesEnabled = Column(
        Boolean, nullable=False, server_default="false"
    )

    #: Is Editing enabled? (Also ensure ALL editDefault fields are set.
    branchesEnabled = Column(Boolean, nullable=False, server_default="false")

    #: Is Editing enabled? (Also ensure ALL editDefault fields are set.
    editEnabled = Column(Boolean, nullable=False, server_default="false")

    #: Default Layer for new shapes
    editDefaultLayerId = Column(Integer, ForeignKey("DispLayer.id"))

    #: Default Level for new shapes
    editDefaultLevelId = Column(Integer, ForeignKey("DispLevel.id"))

    #: Default Color for new shapes
    editDefaultColorId = Column(Integer, ForeignKey("DispColor.id"))

    #: Default Line for new shapes
    editDefaultLineStyleId = Column(Integer, ForeignKey("DispLineStyle.id"))

    #: Default Text for new shapes
    editDefaultTextStyleId = Column(Integer, ForeignKey("DispTextStyle.id"))

    #: Default Vertex/Node/Equipment Coord Set
    editDefaultVertexCoordSetId = Column(
        Integer, ForeignKey("ModelCoordSet.id")
    )
    editDefaultVertexGroupName = Column(String)

    #: Default Edge/Conductor Coord Set
    editDefaultEdgeCoordSetId = Column(Integer, ForeignKey("ModelCoordSet.id"))
    editDefaultEdgeGroupName = Column(String)

    userGroupsAllowed: str = Column(String)
    userGroupsDenied: str = Column(String)

    order = Column(Integer, nullable=False, server_default="0")

    __table_args__ = (
        Index("idxCoordSetModelName", modelSetId, name, unique=True),
        Index("idxCoordSetImportId1", importId1, unique=False),
        Index("idxCoordSetImportId2", importId2, unique=False),
        Index("idxCoordModelSetId", modelSetId, unique=False),
        Index(
            "idxCoordModel_editDefaultLayerId", editDefaultLayerId, unique=False
        ),
        Index(
            "idxCoordModel_editDefaultLevelId", editDefaultLevelId, unique=False
        ),
        Index(
            "idxCoordModel_editDefaultColorId", editDefaultColorId, unique=False
        ),
        Index(
            "idxCoordModel_editDefaultLineStyleId",
            editDefaultLineStyleId,
            unique=False,
        ),
        Index(
            "idxCoordModel_editDefaultTextStyleId",
            editDefaultTextStyleId,
            unique=False,
        ),
        Index(
            "idxCoordModel_editDefaultVertexCoordSetId",
            editDefaultVertexCoordSetId,
            unique=False,
        ),
        Index(
            "idxCoordModel_editDefaultEdgeCoordSetId",
            editDefaultEdgeCoordSetId,
            unique=False,
        ),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def toTuple(self) -> DiagramCoordSetTuple:
        return DiagramCoordSetTuple(
            key=self.key,
            name=self.name,
            backgroundLightColor=self.backgroundLightColor,
        )


@addTupleType
class ModelCoordSetGridSizeTable(DeclarativeBase, Tuple):
    """Coord Set Grid Size Settings

    To match a Z_GRID the display item must be min <= ON < max
    The equal to is on the min side, not the max side

    """

    __tablename__ = "ModelCoordSetGridSize"
    __tupleType__ = diagramTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(Integer, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    xGrid = Column(Integer, nullable=False)
    yGrid = Column(Integer, nullable=False)

    smallestTextSize = Column(Float, nullable=False, server_default="6.0")
    smallestShapeSize = Column(Float, nullable=False, server_default="2.0")

    coordSetId = Column(
        Integer,
        ForeignKey("ModelCoordSet.id", ondelete="CASCADE"),
        nullable=False,
    )
    coordSet = relationship(
        ModelCoordSetTable,
        primaryjoin="ModelCoordSetTable.id==ModelCoordSetGridSizeTable.coordSetId",
    )

    __table_args__ = (
        Index("idx_CoordSetGridSize_key", coordSetId, key, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    DEFAULT = [
        # These defaults are good for Aurora
        dict(
            min=0.0,
            max=0.04,
            key=0,
            xGrid=30000,
            yGrid=30000,
            smallestShapeSize=20,
            smallestTextSize=8,
        ),
        dict(
            min=0.04,
            max=0.1,
            key=1,
            xGrid=10000,
            yGrid=10000,
            smallestShapeSize=20,
            smallestTextSize=8,
        ),
        dict(
            min=0.1,
            max=0.5,
            key=2,
            xGrid=2000,
            yGrid=2000,
            smallestShapeSize=20,
            smallestTextSize=8,
        ),
        dict(
            min=0.5,
            max=1000.0,
            key=3,
            xGrid=1000,
            yGrid=1000,
            smallestShapeSize=2,
            smallestTextSize=4,
        ),
    ]

    def makeGridKey(self, x, y):
        """Make Grid Key

        coordSetId = ModelCoordSet.id
        gridSize = GridSize (above)
        x, y = Grid coordinates, top left
        """
        return "%s|%s.%sx%s" % (self.coordSetId, self.key, x, y)

    @classmethod
    def makeGridKeyStartsWith(cls, coordSetId: int, gridKeySize: int):
        return "%s|%s." % (coordSetId, gridKeySize)

    @classmethod
    def gridSizeKeyFromGridKey(cls, gridKey: str):
        try:
            return int(gridKey.split("|")[1].split(".")[0])
        except:
            logger.error("Grid key [%s] is malformed", gridKey)
            raise


def makeDispGroupGridKey(coordSetId: int):
    """Make Disp Group Grid Key

    Make the special disp group grid key name.
    This is used to store all of the DispGroups that are not specifically stored in a
    grid, with the DispGroupPtr that uses it.

    """
    return "%s|dispgroup" % coordSetId


def getOrCreateModelSet(session, modelSetKey):
    qry = session.query(ModelSetTable).filter(ModelSetTable.key == modelSetKey)
    if not qry.count():
        session.add(ModelSetTable(name=modelSetKey, key=modelSetKey))
        try:
            session.commit()
        except IntegrityError:
            return qry.one()

    return qry.one()


def getOrCreateCoordSet(session, modelSetKey, coordSetKey):
    modelSet = getOrCreateModelSet(session, modelSetKey)

    qry = (
        session.query(ModelCoordSetTable)
        .filter(ModelCoordSetTable.modelSetId == modelSet.id)
        .filter(ModelCoordSetTable.key == coordSetKey)
    )

    if not qry.count():
        coordSet = ModelCoordSetTable(
            modelSetId=modelSet.id, name=coordSetKey, key=coordSetKey
        )
        session.add(coordSet)

        for gridSize in ModelCoordSetGridSizeTable.DEFAULT:
            newGrid = ModelCoordSetGridSizeTable(**gridSize)
            newGrid.coordSet = coordSet
            session.add(newGrid)

        try:
            session.commit()
        except IntegrityError:
            return qry.one()

    return qry.one()

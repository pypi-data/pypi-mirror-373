import logging
import time
from collections import defaultdict
from collections import namedtuple
from textwrap import dedent
from typing import Annotated
from typing import Dict
from typing import List
from typing import Optional

from sqlalchemy import and_
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text
from vortex.DeferUtil import noMainThread
from vortex.Payload import Payload

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndex
from peek_plugin_diagram._private.storage.GridKeyIndex import (
    GridKeyIndexCompiled,
)
from peek_plugin_diagram._private.storage.Lookups import lookupKeyToId
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable
from peek_plugin_diagram._private.storage.ModelSet import (
    ModelCoordSetGridSizeTable,
)
from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable
from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.tuples.grid.GridTuple import GridTuple
from peek_plugin_diagram._private.worker.utils.ShapeLookupLinker import (
    ShapeLookupLinker,
)
from peek_plugin_diagram.tuples.grids.DecodedCompiledGridTuple import (
    DecodedCompiledGridTuple,
)
from peek_plugin_diagram.tuples.grids.GridKeyTuple import GridKeyTuple
from peek_plugin_diagram.worker.canvas_shapes.ShapeBase import ShapeBase
from peek_plugin_diagram.tuples.model.DiagramCoordSetTuple import (
    DiagramCoordSetTuple,
)

logger = logging.getLogger(__name__)


class WorkerDiagramGridApiImpl:
    _DEBUG_LOGGING = False

    @classmethod
    def getModelCoordSet(
        self, modelSetKey: str, coordSetKey: str
    ) -> DiagramCoordSetTuple:
        ormSession = TaskDbConn.getDbSession()
        try:
            row = (
                ormSession.query(ModelCoordSetTable)
                .join(
                    ModelSetTable,
                    onclause=ModelCoordSetTable.modelSetId == ModelSetTable.id,
                )
                .filter(ModelSetTable.name == modelSetKey)
                .filter(ModelCoordSetTable.key == coordSetKey)
                .one()
            )

            return row.toTuple()

        finally:
            ormSession.close()

    @classmethod
    def getGridKeys(
        cls,
        modelSetKey: str,
        coordSetKey: str,
        boundingBox: Annotated[List[float], 4] = None,
        xGridCountPadding: int = 0,
        yGridCountPadding: int = 0,
    ) -> List[GridKeyTuple]:
        session = TaskDbConn.getDbSession()
        try:
            query = text(
                dedent(
                    f"""
                WITH gridInfo AS (
                    SELECT
                        m1."xGrid" AS "xGrid",
                        m1."yGrid" AS "yGrid",
                        (mcs.id || '|' || m1.key || '.%')::text AS pattern
                    FROM
                        pl_diagram."ModelCoordSetGridSize" AS m1
                        JOIN pl_diagram."ModelCoordSet" AS mcs ON m1."coordSetId" = mcs.id
                        JOIN pl_diagram."ModelSet" AS ms ON ms.id = mcs."modelSetId"
                    WHERE
                        mcs."key" = '{coordSetKey}'
                        AND ms.key = '{modelSetKey}'
                    ORDER BY
                        m1."max" DESC
                    LIMIT 1
                )
                SELECT
                    "gridKey" AS gridKey,
                    (
                        SELECT
                            "xGrid"
                        FROM
                            gridInfo
                    ) AS width,
                    (
                        SELECT
                            "yGrid"
                        FROM
                            gridInfo
                    ) AS height,
                    count(*) AS shapeCount
                FROM
                    pl_diagram."GridKeyIndex" AS gi
                WHERE
                    gi."gridKey" LIKE (
                        SELECT
                            pattern
                        FROM
                            gridInfo
                    )
                GROUP BY
                    gi."gridKey";
            """
                )
            )

            rows = session.execute(query)

            if boundingBox is not None and len(boundingBox) == 4:
                gridSizeRow = (
                    session.query(ModelCoordSetGridSizeTable)
                    .join(
                        ModelCoordSetTable,
                        and_(
                            ModelCoordSetTable.id
                            == ModelCoordSetGridSizeTable.coordSetId
                        ),
                    )
                    .join(
                        ModelSetTable,
                        and_(ModelSetTable.id == ModelCoordSetTable.modelSetId),
                    )
                    .filter(
                        and_(
                            ModelSetTable.key == modelSetKey,
                            ModelCoordSetTable.key == coordSetKey,
                        )
                    )
                    .order_by(ModelCoordSetGridSizeTable.max.desc())
                    .first()
                )

                # if we have no shapes in this area of the diagram, then return
                # an array of no grid keys.
                if not gridSizeRow:
                    return []

                xGrid = gridSizeRow.xGrid
                yGrid = gridSizeRow.yGrid

                topLeftX = int(boundingBox[0] / xGrid)
                topLeftY = int(boundingBox[1] / yGrid)
                bottomRightX = int(boundingBox[2] / xGrid)
                bottomRightY = int(boundingBox[3] / yGrid)

                topLeftX -= xGridCountPadding
                topLeftY -= yGridCountPadding
                bottomRightX += xGridCountPadding
                bottomRightY += yGridCountPadding

            gridKeys = []
            for row in rows:
                _, _, xy = row[0].partition(".")  # gridKey
                x, _, y = xy.partition("x")

                x = int(x)
                y = int(y)

                if (
                    boundingBox is not None
                    and (topLeftX <= x <= bottomRightX)
                    and (topLeftY <= y <= bottomRightY)
                ):
                    g = GridKeyTuple(
                        gridKey=row[0],
                        width=float(row[1]),
                        height=float(row[2]),
                        shapeCount=int(row[3]),
                        modelSetKey=modelSetKey,
                        coordSetKey=coordSetKey,
                    )
                    gridKeys.append(g)
                elif boundingBox is None:
                    gridKeys.append(
                        GridKeyTuple(
                            gridKey=row[0],
                            width=float(row[1]),
                            height=float(row[2]),
                            shapeCount=int(row[3]),
                            modelSetKey=modelSetKey,
                            coordSetKey=coordSetKey,
                        )
                    )

            return gridKeys

        finally:
            session.close()

    @classmethod
    def getShapesByGridKeys(
        cls, gridKeys: List[str]
    ) -> Dict[str, DecodedCompiledGridTuple]:
        """get shapes filtered by grid keys in one query to database

        This guarantees states of all shapes are at the same time

        :param gridKeys: a list of gridKeys in str
        :return: a dict that maps gridKey to a list of DecodedCompiledGridTuple
        """
        s = time.monotonic()
        session = TaskDbConn.getDbSession()
        try:
            query = session.query(GridKeyIndexCompiled).filter(
                GridKeyIndexCompiled.gridKey.in_(gridKeys)
            )

            rows = query.all()
            decodedCompiledGridTuplesByGridKey = {}

            for row in rows:
                # get encoded chunk and decode it as `Payload`
                gridTuplesPayload: Payload = row.decodedDataBlocking
                # get the GridTuple from Payload
                gridTuple: GridTuple = gridTuplesPayload.tuples[0]

                decodedCompiledGridTuplesByGridKey[gridTuple.gridKey] = (
                    gridTuple.toDecodedCompiledGridTuple()
                )

            return decodedCompiledGridTuplesByGridKey
        finally:
            session.close()

    @classmethod
    def linkShapes(
        cls,
        decodedCompiledGridTuplesByGridKey: Dict[str, DecodedCompiledGridTuple],
    ):
        shapeLookupLinker = ShapeLookupLinker()
        shapeLookupLinker.loadLookups()

        for (
            gridKey,
            decodedCompiledGridTuple,
        ) in decodedCompiledGridTuplesByGridKey.items():
            shapeLookupLinker.linkShapesToLookups(
                decodedCompiledGridTuple.shapes
            )

    @classmethod
    def compileShapes(
        cls,
        decodedCompiledGridTuples,
        levelsOrderedByOrder,
        layersOrderedByOrder,
        shapeSelectionZoomLevel,
        enabledLayerKeys: Optional[list[str]] = None,
        enabledBranchKeys: Optional[list[str]] = None,
    ):
        """an equivalent of PeekCanvasModel._compileDisps()

        :param decodedCompiledGridTuples: a list of decodedCompiledGridTuples
                which contains compiled shapes in a grid
        :param levelsOrderedByOrder: a list of levels already ordered by
        tuplefield `order`
        :param layersOrderedByOrder: a list of layers already ordered by
        tuplefield `order`
        :param shapeSelectionZoomLevel: a zoom level to filter out shapes
        that are displayed above the zoom level
        :return: a list of dicts of shapes that are ready for factory renderer
        """
        # levelsOrderedByOrder = cls._getLevelsOrderedByOrder(
        #     coordSetKey=coordSetKey
        # )
        #
        # layersOrderedByOrder = cls._getLayersOrderedByOrder(
        #     modelSetKey=modelSetKey
        # )

        dispHashIdsAdded = set()
        viewingBranchesActive = bool(enabledBranchKeys)

        # These are overrides
        if enabledLayerKeys:
            enabledLayerKeys = set(enabledLayerKeys)
        else:
            enabledLayerKeys = set()
            for layer in layersOrderedByOrder:
                if layer.calculateEffectiveVisibility():
                    enabledLayerKeys.add(layer.key)

        if not enabledBranchKeys:
            branchIdsActive = set()
        else:
            session = TaskDbConn.getDbSession()
            try:
                branchIdsActive = set(
                    [
                        o.id
                        for o in session.query(BranchIndex.id).filter(
                            BranchIndex.key.in_(enabledBranchKeys)
                        )
                    ]
                )
            finally:
                session.close()

        for gridOrBranch in decodedCompiledGridTuples:
            for shape in gridOrBranch.shapes:
                # TODO Restrict for Branch Stage
                # If the branch is showing, and it replaces a hash,
                # then add the hash it replaces
                replacesHashId = ShapeBase.replacesHashId(shape)
                if (
                    ShapeBase.branchId(shape) in branchIdsActive
                    and replacesHashId
                ):
                    dispHashIdsAdded.add(replacesHashId)

        dispIndexByGridKey = defaultdict(int)
        disps = []
        for level in levelsOrderedByOrder:
            for layer in layersOrderedByOrder:
                if layer.key not in enabledLayerKeys:
                    continue

                for decodedCompiledGridTuple in decodedCompiledGridTuples:
                    gridKey = decodedCompiledGridTuple.gridKey

                    # default is 0 if key doesn't exist
                    nextIndex = dispIndexByGridKey[gridKey]

                    shapes = decodedCompiledGridTuple.shapes

                    if nextIndex >= len(shapes):
                        continue

                    # while nextIndex < len(shapes):
                    for i in range(nextIndex, len(shapes), 1):
                        nextIndex = i
                        shape = shapes[i]

                        # Filter out overlay disps if we need to
                        if viewingBranchesActive and ShapeBase.isOverlay(shape):
                            continue

                        # for idx, shape in enumerate(shapes):
                        # Level first, as per the sortDisps function
                        shapeLevel = ShapeBase.level(shape)
                        if shapeLevel.order < level.order:
                            continue
                        if level.order < shapeLevel.order:
                            break

                        shapeLevelId = lookupKeyToId(shapeLevel.key)
                        levelId = lookupKeyToId(level.key)
                        # Levels can have duplicate order
                        if shapeLevelId < levelId:
                            continue
                        if levelId < shapeLevelId:
                            break

                        # Then Layer
                        shapeLayer = ShapeBase.layer(shape)
                        if shapeLayer.order < layer.order:
                            continue
                        if layer.order < shapeLayer.order:
                            break

                        shapeLayerId = lookupKeyToId(shapeLayer.key)
                        layerId = lookupKeyToId(layer.key)
                        # Levels can have duplicate order
                        if shapeLayerId < layerId:
                            continue
                        if layerId < shapeLayerId:
                            break

                        # If we should filter based on zoom level, then do that.
                        if not (
                            shapeSelectionZoomLevel is None
                            or shapeLevel.minZoom
                            <= shapeSelectionZoomLevel
                            <= shapeLevel.maxZoom
                        ):
                            continue

                        # If the disp has already been added or is being replaced
                        # by a branch, then skip this one
                        if ShapeBase.hashId(shape) in dispHashIdsAdded:
                            continue

                        # Is the branch showed from the "View Branches" menu
                        isBranchViewable = (
                            ShapeBase.branchId(shape) in branchIdsActive
                        )

                        # If this is not apart of a branch, or ...
                        if (
                            ShapeBase.branchId(shape) is None
                            or isBranchViewable
                        ):
                            disps.append(shape)
                            dispHashIdsAdded.add(ShapeBase.hashId(shape))

                    dispIndexByGridKey[gridKey] = nextIndex

        return disps

    @classmethod
    def getGridKeyTuplesFromShapeKeys(
        cls, modelSetKey, coordSetKey, shapeKeys, smallestGridKeySize=False
    ) -> List[GridKeyTuple]:
        _GridData = namedtuple("_GridData", ("gridKey", "width", "height"))

        noMainThread()

        gridKeyIndexTable = GridKeyIndex.__table__
        dispBaseTable = DispBase.__table__

        # Ensure there are no duplicate keys or empty keys
        shapeKeys = list(set(filter(lambda k: k, shapeKeys)))

        ormSession = TaskDbConn.getDbSession()
        try:
            coordSetId = (
                ormSession.query(ModelCoordSetTable.id)
                .filter(
                    ModelCoordSetTable.key == coordSetKey
                    and ModelCoordSetTable.modelSet.key == modelSetKey
                )
                .scalar()
            )

            gridKeysIterable = set()

            # Start a transaction so we have consistent results.
            CHUNK_SIZE = 1000

            for i in range(0, len(shapeKeys), CHUNK_SIZE):
                chunkedShapeKeys = shapeKeys[i : i + CHUNK_SIZE]
                sql = (
                    select(gridKeyIndexTable.c.gridKey)
                    .select_from(
                        gridKeyIndexTable.join(
                            dispBaseTable,
                            dispBaseTable.c.id == gridKeyIndexTable.c.dispId,
                        )
                    )
                    .where(dispBaseTable.c.key.in_(chunkedShapeKeys))
                    .distinct()
                )

                gridKeysIterable.update(
                    [row.gridKey for row in ormSession.execute(sql)]
                )

            # Query for the grid size data
            gridKeySizesByKey = {
                gs.key: gs
                for gs in ormSession.query(ModelCoordSetGridSizeTable).filter(
                    ModelCoordSetGridSizeTable.coordSetId == coordSetId
                )
            }

            # If we just want the smallest grids, filter for them
            if smallestGridKeySize:
                maxKey = max([i.key for i in gridKeySizesByKey.values()])

                ## Filter the grid sizes
                gridKeySizesByKey = {maxKey: gridKeySizesByKey[maxKey]}

                # Filter the grids
                startsWithStr = (
                    ModelCoordSetGridSizeTable.makeGridKeyStartsWith(
                        coordSetId, maxKey
                    )
                )

                gridKeysIterable = list(
                    filter(
                        lambda gridKey: gridKey.startswith(startsWithStr),
                        gridKeysIterable,
                    )
                )

            # Query for the shape counts and create the GridKeyTuple
            sql = (
                select(
                    gridKeyIndexTable.c.gridKey,
                    func.count(gridKeyIndexTable.c.gridKey).label("shapeCount"),
                )
                .where(gridKeyIndexTable.c.gridKey.in_(gridKeysIterable))
                .group_by(gridKeyIndexTable.c.gridKey)
            )

            gridKeyTuples = []

            for row in ormSession.execute(sql):
                gridSize = gridKeySizesByKey[
                    ModelCoordSetGridSizeTable.gridSizeKeyFromGridKey(
                        row.gridKey
                    )
                ]

                gridKeyTuples.append(
                    GridKeyTuple(
                        gridKey=row.gridKey,
                        width=float(gridSize.xGrid),
                        height=float(gridSize.yGrid),
                        shapeCount=row.shapeCount,
                        modelSetKey=modelSetKey,
                        coordSetKey=coordSetKey,
                    )
                )

            return gridKeyTuples

        finally:
            ormSession.close()

    @classmethod
    def filterShapesByShapeKey(
        cls, shapes: list[dict], filterForKeys: set[str]
    ) -> list[dict]:
        assert isinstance(filterForKeys, set), (
            "Please convert filterForKeys "
            "to a set before passing it to filterShapesByShapeKey"
        )
        if cls._DEBUG_LOGGING:
            logger.debug(
                "filterShapesByShapeKey: Started,"
                " with %s shapes and %s filter keys",
                len(shapes),
                len(filterForKeys),
            )

        # Index the shapes so we know which shapes belong to which group id
        shapesByGroupId: dict[int, list[tuple[int, dict]]] = defaultdict(list)
        for index, shape in enumerate(shapes):
            groupId = ShapeBase.groupId(shape)
            if groupId is not None:
                shapesByGroupId[groupId].append((index, shape))

        if cls._DEBUG_LOGGING:
            logger.debug(
                "filterShapesByShapeKey: Completed indexing shapes by groupId, We've found %s groupIds",
                len(shapesByGroupId),
            )

        # This is all the shapes we want to collect
        shapeIndexes = set()

        # This is the list of shape groups we need to include the group
        # members for
        groupShapeParentIds = []

        # First, iterate over the shapes and filter for the shapes by keys
        for index, shape in enumerate(shapes):
            if ShapeBase.key(shape) in filterForKeys:
                shapeIndexes.add(index)
                groupShapeParentIds.append(ShapeBase.id(shape))

                groupId = ShapeBase.groupId(shape)
                if groupId:
                    groupShapeParentIds.append(groupId)

        if cls._DEBUG_LOGGING:
            logger.debug(
                "filterShapesByShapeKey: Completed filtering by key, %s shapes selected",
                len(shapeIndexes),
            )

        # Next we include the shapes that are group memebers of the shapes in
        # the last loop.
        # We also include those shapes in our next check and include those
        # shapes members - groups can have groups in them.
        loop = 1
        while groupShapeParentIds:
            nextGroupShapeParentIds = []

            for groupId in groupShapeParentIds:
                memberIndexShapeTuples = shapesByGroupId.get(groupId, [])
                for index, shape in memberIndexShapeTuples:
                    shapeIndexes.add(index)
                    nextGroupShapeParentIds.append(ShapeBase.id(shape))

            if cls._DEBUG_LOGGING:
                logger.debug(
                    "filterShapesByShapeKey: Completed filtering for"
                    " level %s group members"
                    " of %s groups,"
                    " found %s shapes",
                    loop,
                    len(groupShapeParentIds),
                    len(nextGroupShapeParentIds),
                )

            groupShapeParentIds = nextGroupShapeParentIds
            loop += 1

        if cls._DEBUG_LOGGING:
            logger.debug(
                "filterShapesByShapeKey: Completed, returning %s shapes.",
                len(shapeIndexes),
            )

        # return sortedFilteredShapes
        return [shapes[index] for index in sorted(shapeIndexes)]

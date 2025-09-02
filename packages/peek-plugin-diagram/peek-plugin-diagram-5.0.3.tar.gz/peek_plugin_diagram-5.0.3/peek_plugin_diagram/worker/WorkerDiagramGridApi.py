from typing import Annotated
from typing import Dict
from typing import List
from typing import Optional

from vortex.Tuple import Tuple

from peek_plugin_diagram.tuples.grids.GridKeyTuple import GridKeyTuple
from peek_plugin_diagram.tuples.model.DiagramCoordSetTuple import (
    DiagramCoordSetTuple,
)


class WorkerDiagramGridApi:
    @classmethod
    def getModelCoordSet(
        self, modelSetKey: str, coordSetKey: str
    ) -> DiagramCoordSetTuple:
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.getModelCoordSet(
            modelSetKey=modelSetKey, coordSetKey=coordSetKey
        )

    @classmethod
    def getGridKeys(
        cls,
        modelSetKey: str,
        coordSetKey: str,
        boundingBox: Annotated[List[float], 4] = None,
        xGridCountPadding: int = 0,
        yGridCountPadding: int = 0,
    ):
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.getGridKeys(
            modelSetKey=modelSetKey,
            coordSetKey=coordSetKey,
            boundingBox=boundingBox,
            xGridCountPadding=xGridCountPadding,
            yGridCountPadding=yGridCountPadding,
        )

    @classmethod
    def getShapesByGridKeys(cls, gridKeys) -> Dict[str, Tuple]:
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.getShapesByGridKeys(gridKeys=gridKeys)

    @classmethod
    def linkShapes(cls, decodedCompiledGridTuplesByGridKey: Dict):
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.linkShapes(
            decodedCompiledGridTuplesByGridKey
        )

    @classmethod
    def compileShapes(
        cls,
        decodedCompiledGridTuples: List,
        levelsOrderedByOrder,
        layersOrderedByOrder,
        shapeSelectionZoomLevel=2.0,
        enabledLayerKeys: Optional[list[str]] = None,
        enabledBranchKeys: Optional[list[str]] = None,
    ):
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.compileShapes(
            decodedCompiledGridTuples=decodedCompiledGridTuples,
            levelsOrderedByOrder=levelsOrderedByOrder,
            layersOrderedByOrder=layersOrderedByOrder,
            shapeSelectionZoomLevel=shapeSelectionZoomLevel,
            enabledLayerKeys=enabledLayerKeys,
            enabledBranchKeys=enabledBranchKeys,
        )

    @classmethod
    def getGridKeyTuplesFromShapeKeys(
        cls,
        modelSetKey,
        coordSetKey,
        shapeKeys: list[str],
        smallestGridKeySize: Optional[bool] = False,
    ) -> List[GridKeyTuple]:
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.getGridKeyTuplesFromShapeKeys(
            modelSetKey=modelSetKey,
            coordSetKey=coordSetKey,
            shapeKeys=shapeKeys,
            smallestGridKeySize=smallestGridKeySize,
        )

    @classmethod
    def filterShapesByShapeKey(
        cls, shapes: list[dict], filterForKeys: set[str]
    ) -> list[dict]:
        from peek_plugin_diagram._private.worker.api.WorkerDiagramGridApiImpl import (
            WorkerDiagramGridApiImpl,
        )

        return WorkerDiagramGridApiImpl.filterShapesByShapeKey(
            shapes=shapes, filterForKeys=filterForKeys
        )

from typing import List

from vortex.Tuple import Tuple

from peek_plugin_diagram._private.worker.api.WorkerDiagramLookupApiImpl import (
    WorkerDiagramLookupApiImpl,
)
from peek_plugin_diagram.tuples.lookup_tuples.ShapeLayerTuple import (
    ShapeLayerTuple,
)


class WorkerDiagramLookupApi:
    @classmethod
    def getColors(cls) -> List[Tuple]:
        return WorkerDiagramLookupApiImpl.getColors()

    @classmethod
    def getLineStyles(cls) -> List[Tuple]:
        return WorkerDiagramLookupApiImpl.getLineStyles()

    @classmethod
    def getTextStyles(cls) -> List[Tuple]:
        return WorkerDiagramLookupApiImpl.getTextStyles()

    @classmethod
    def getLayers(cls) -> List[ShapeLayerTuple]:
        return WorkerDiagramLookupApiImpl.getLayers()

    @classmethod
    def getLevels(cls) -> List[Tuple]:
        return WorkerDiagramLookupApiImpl.getLevels()

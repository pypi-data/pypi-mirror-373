import logging

from twisted.internet.defer import Deferred

from peek_plugin_diagram._private.storage.ModelSet import (
    ModelCoordSetTable,
    ModelSetTable,
)
from peek_plugin_diagram.server.DiagramViewerApiABC import DiagramViewerApiABC
from peek_plugin_diagram.tuples.model.DiagramCoordSetTuple import (
    DiagramCoordSetTuple,
)
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class DiagramViewerApi(DiagramViewerApiABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def getCoordSets(
        self, modelSetKey: str
    ) -> Deferred[list[DiagramCoordSetTuple]]:
        ormSession = self._ormSessionCreator()
        try:
            all = (
                ormSession.query(ModelCoordSetTable)
                .join(ModelSetTable)
                .filter(ModelSetTable.name == modelSetKey)
                .all()
            )

            coordSetTuples = []
            for obj in all:
                coordSetTuples.append(obj.toTuple())

            return coordSetTuples

        finally:
            ormSession.close()

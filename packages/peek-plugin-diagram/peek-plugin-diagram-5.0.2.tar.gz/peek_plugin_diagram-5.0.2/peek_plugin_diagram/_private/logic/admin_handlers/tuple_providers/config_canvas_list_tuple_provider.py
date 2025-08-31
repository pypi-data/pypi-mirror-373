import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSetTable
from peek_plugin_diagram._private.tuples.admin.config_canvas_list_tuple import (
    ConfigCanvasListTuple,
)


logger = logging.getLogger(__name__)


class ConfigCanvasListTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:
        modelSetId = tupleSelector.selector["modelSetId"]

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ConfigCanvasListTuple(
                    id=t.id,
                    key=t.key,
                    name=t.name,
                    modelSetId=t.modelSetId,
                    modelSetKey=t.modelSet.key,
                    enabled=t.enabled,
                    dispGroupTemplatesEnabled=t.dispGroupTemplatesEnabled,
                    edgeTemplatesEnabled=t.edgeTemplatesEnabled,
                )
                for t in dbSession.query(ModelCoordSetTable)
                .filter(ModelCoordSetTable.modelSetId == modelSetId)
                .all()
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg

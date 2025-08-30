import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.tuples.admin.config_level_lookup_list_tuple import (
    ConfigLevelLookupListTuple,
)


logger = logging.getLogger(__name__)


class ConfigLevelLookupListTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:
        canvasId = tupleSelector.selector["canvasId"]

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ConfigLevelLookupListTuple(
                    id=t.id,
                    modelSetId=t.coordSet.modelSetId,
                    modelSetKey=t.coordSet.modelSet.key,
                    canvasSetId=canvasId,
                    canvasSetKey=t.coordSet.key,
                    name=t.name,
                    importHash=t.importHash,
                )
                for t in dbSession.query(DispLevelTable)
                .filter(DispLevelTable.coordSetId == canvasId)
                .order_by(DispLevelTable.name)
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg

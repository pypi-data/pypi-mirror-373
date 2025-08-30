import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.tuples.admin.config_color_lookup_list_tuple import (
    ConfigColorLookupListTuple,
)


logger = logging.getLogger(__name__)


class ConfigColorLookupListTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:
        modelSetId = tupleSelector.selector["modelSetId"]

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ConfigColorLookupListTuple(
                    id=t.id,
                    modelSetId=modelSetId,
                    modelSetKey=t.modelSet.key,
                    name=t.name,
                    importHash=t.importHash,
                )
                for t in dbSession.query(DispColorTable)
                .filter(DispColorTable.modelSetId == modelSetId)
                .order_by(DispColorTable.name)
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg

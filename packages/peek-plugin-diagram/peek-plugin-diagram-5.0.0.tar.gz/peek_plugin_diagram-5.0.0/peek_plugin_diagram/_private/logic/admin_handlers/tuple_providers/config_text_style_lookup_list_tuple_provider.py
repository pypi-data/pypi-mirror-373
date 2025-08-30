import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.tuples.admin.config_text_style_lookup_list_tuple import (
    ConfigTextStyleLookupListTuple,
)


logger = logging.getLogger(__name__)


class ConfigTextStyleLookupListTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:
        modelSetId = tupleSelector.selector["modelSetId"]

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ConfigTextStyleLookupListTuple(
                    id=t.id,
                    modelSetId=modelSetId,
                    modelSetKey=t.modelSet.key,
                    name=t.name,
                    importHash=t.importHash,
                )
                for t in dbSession.query(DispTextStyleTable)
                .filter(DispTextStyleTable.modelSetId == modelSetId)
                .order_by(DispTextStyleTable.name)
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg

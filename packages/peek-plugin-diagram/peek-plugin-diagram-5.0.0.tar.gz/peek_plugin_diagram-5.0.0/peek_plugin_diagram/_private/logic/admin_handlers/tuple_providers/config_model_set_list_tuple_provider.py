import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable
from peek_plugin_diagram._private.tuples.admin.config_model_list_tuple import (
    ConfigModelSetListTuple,
)


logger = logging.getLogger(__name__)


class ConfigModelSetListTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> bytes:

        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                ConfigModelSetListTuple(id=t.id, key=t.key, name=t.name)
                for t in dbSession.query(ModelSetTable)
            ]
        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg

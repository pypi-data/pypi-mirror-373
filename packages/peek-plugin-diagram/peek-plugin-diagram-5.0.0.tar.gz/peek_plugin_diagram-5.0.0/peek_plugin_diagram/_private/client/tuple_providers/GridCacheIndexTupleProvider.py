import logging
from typing import Union

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.client.controller.GridCacheController import (
    GridCacheController,
)

logger = logging.getLogger(__name__)


class GridCacheIndexTupleProvider(TuplesProviderABC):
    def __init__(self, gridCacheController: GridCacheController):
        self._gridCacheController = gridCacheController

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        emptyPayloadVortexMsg = PayloadEnvelope(
            filt, encodedPayload=Payload().toEncodedPayload()
        ).toVortexMsg()

        index = tupleSelector.selector.get("index")

        if index is None:
            # Make it backwards compatible with v3.3.0 and below
            start = tupleSelector.selector.get("start")
            count = tupleSelector.selector.get("count")

            if count is not None and start is not None:
                count = count - start

            if count is None or count != 5000:
                return emptyPayloadVortexMsg

            index = start / count

        try:
            encodedPayload = (
                self._gridCacheController.offlineUpdateDateByChunkKeyPayload(
                    index
                )
            )
        except IndexError:
            return emptyPayloadVortexMsg

        payloadEnvelope = PayloadEnvelope(filt, encodedPayload=encodedPayload)
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg

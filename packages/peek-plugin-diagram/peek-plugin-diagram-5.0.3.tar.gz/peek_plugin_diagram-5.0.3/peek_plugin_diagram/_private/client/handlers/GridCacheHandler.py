import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict
from typing import List

import pytz
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import vortexLogFailure
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory, NoVortexException

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.client.controller.GridCacheController import (
    GridCacheController,
)
from peek_plugin_diagram._private.client.controller.GridCacheController import (
    clientGridUpdateFromServerFilt,
)
from peek_plugin_diagram._private.logic.client_handlers.rpc.ClientGridLoaderRpc import (
    ClientGridLoaderRpc,
)
from peek_plugin_diagram._private.storage.GridKeyIndex import (
    GridKeyIndexCompiled,
)
from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import (
    EncodedGridTuple,
)

logger = logging.getLogger(__name__)

clientGridWatchUpdateFromDeviceFilt = {"key": "clientGridWatchUpdateFromDevice"}
clientGridWatchUpdateFromDeviceFilt.update(diagramFilt)

#: This the type of the data that we get when the clients observe new grids.
DeviceGridT = Dict[str, datetime]


# ModelSet HANDLER
class GridCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = GridKeyIndexCompiled
    _updateFromDeviceFilt: Dict = clientGridWatchUpdateFromDeviceFilt
    _updateFromLogicFilt: Dict = clientGridUpdateFromServerFilt
    _logger: logging.Logger = logger

    def __init__(self, cacheController: GridCacheController, clientId: str):
        """App Grid Handler

        This class handles the custom needs of the desktop/mobile
         apps observing grids.

        """
        ACICacheHandlerABC.__init__(self, cacheController, clientId)

        # We need to know who is watching what so we can tell the server.
        self._observedGridKeysByVortexUuid = defaultdict(list)
        self._observedVortexUuidsByGridKey = defaultdict(list)

        # We're not using this
        del self._uuidsObserving

    # ---------------
    # Filter out offline vortexes

    def _filterOutOfflineVortexes(self):
        # TODO, Change this to observe offline vortexes
        # This depends on the VortexFactory offline observable implementation.
        # Which is incomplete at this point :-|

        vortexUuids = set(VortexFactory.getRemoteVortexUuids())
        vortexUuidsToRemove = (
            set(self._observedGridKeysByVortexUuid) - vortexUuids
        )

        if not vortexUuidsToRemove:
            return

        for vortexUuid in vortexUuidsToRemove:
            del self._observedGridKeysByVortexUuid[vortexUuid]

        self._rebuildStructs()

    # ---------------
    # Process update from the server

    @inlineCallbacks
    def notifyOfUpdate(self, gridKeys: List[str]):
        """Notify of Grid Updates

        This method is called by the client.GridCacheController when it receives updates
        from the server.

        """
        self._filterOutOfflineVortexes()

        def cratePayloadEnvelope():
            payloadEnvelope = PayloadEnvelope()
            payloadEnvelope.data = []
            return payloadEnvelope

        payloadsByVortexUuid = defaultdict(cratePayloadEnvelope)

        for gridKey in gridKeys:
            gridTuple = self._cacheController.encodedChunk(gridKey)
            if not gridTuple:
                gridTuple = EncodedGridTuple()
                gridTuple.gridKey = gridKey

            vortexUuids = self._observedVortexUuidsByGridKey.get(gridKey, [])

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug(
                    "Sending unsolicited grid %s to vortex %s",
                    gridKey,
                    vortexUuid,
                )
                payloadsByVortexUuid[vortexUuid].data.append(gridTuple)

        # Send the updates to the clients
        for vortexUuid, payloadEnvelope in payloadsByVortexUuid.items():
            payloadEnvelope.filt = clientGridWatchUpdateFromDeviceFilt

            vortexMsg = yield payloadEnvelope.toVortexMsgDefer(
                base64Encode=False
            )

            try:
                yield VortexFactory.sendVortexMsg(
                    vortexMsg, destVortexUuid=vortexUuid
                )

            except NoVortexException:
                pass
            except Exception as e:
                self._logger.exception(e)

    # ---------------
    # Process observes from the devices

    @inlineCallbacks
    def _processObserve(
        self,
        payloadEnvelope: PayloadEnvelope,
        vortexUuid: str,
        sendResponse: SendVortexMsgResponseCallable,
        **kwargs,
    ):
        cacheAll = payloadEnvelope.filt.get("cacheAll") is True

        payload = yield payloadEnvelope.decodePayloadDefer()

        lastUpdateByGridKey: DeviceGridT = payload.tuples[0]

        if not cacheAll:
            gridKeys = list(lastUpdateByGridKey.keys())
            self._observedGridKeysByVortexUuid[vortexUuid] = gridKeys
            self._rebuildStructs()

        yield self._replyToObserve(
            payload.filt,
            lastUpdateByGridKey,
            sendResponse,
            vortexUuid=vortexUuid,
            cacheAll=cacheAll,
        )

    def _rebuildStructs(self) -> None:
        """Rebuild Structs

        Rebuild the reverse index of uuids by grid key.

        :returns: None
        """
        # Rebuild the other reverse lookup
        newDict = defaultdict(list)

        for vortexUuid, gridKeys in self._observedGridKeysByVortexUuid.items():
            for gridKey in gridKeys:
                newDict[gridKey].append(vortexUuid)

        keysChanged = set(self._observedVortexUuidsByGridKey) != set(newDict)

        self._observedVortexUuidsByGridKey = newDict

        # Notify the server that this client service is watching different grids.
        if keysChanged:
            d = ClientGridLoaderRpc.updateClientWatchedGrids(
                clientId=self._clientId,
                gridKeys=list(self._observedVortexUuidsByGridKey),
            )
            d.addErrback(vortexLogFailure, logger, consumeError=False)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(
        self,
        filt,
        lastUpdateByGridKey: DeviceGridT,
        sendResponse: SendVortexMsgResponseCallable,
        vortexUuid: str,
        cacheAll=False,
    ) -> None:
        """Reply to Observe

        The client has told us that it's observing a new set of grids, and the lastUpdate
        it has for each of those grids. We will send them the grids that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByGridKey: The dict of gridKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        startTime = datetime.now(pytz.utc)
        gridTuplesToSend = []
        updateCount = 0
        sameCount = 0
        deletedCount = 0

        # Check and send any updates
        for gridKey, lastUpdate in lastUpdateByGridKey.items():
            # NOTE: lastUpdate can be null.
            gridTuple = self._cacheController.encodedChunk(gridKey)

            # Last update is not null, we need to send an empty grid.
            if not gridTuple:
                deletedCount += 1
                gridTuple = EncodedGridTuple()
                gridTuple.gridKey = gridKey
                gridTuple.lastUpdate = lastUpdate
                gridTuple.encodedGridTuple = None
                gridTuplesToSend.append(gridTuple)

                if self._DEBUG_LOGGING:
                    logger.debug(
                        "Grid %s is no longer in the cache, %s",
                        gridKey,
                        lastUpdate,
                    )

            elif gridTuple.lastUpdate == lastUpdate:
                sameCount += 1
                if self._DEBUG_LOGGING:
                    logger.debug(
                        "Grid %s matches the cache, %s", gridKey, lastUpdate
                    )

            else:
                updateCount += 1
                gridTuplesToSend.append(gridTuple)
                if self._DEBUG_LOGGING:
                    logger.debug(
                        "Sending grid %s from the cache, %s",
                        gridKey,
                        lastUpdate,
                    )

            if len(gridTuplesToSend) == 5 and not cacheAll:
                yield self._sendData(
                    sendResponse, filt, cacheAll, gridTuplesToSend
                )
                gridTuplesToSend = []

        yield self._sendData(sendResponse, filt, cacheAll, gridTuplesToSend)

        logger.debug(
            "Sent %s updates and %s deletes, %s matched/not sent"
            " to %s in %s",
            updateCount,
            deletedCount,
            sameCount,
            vortexUuid,
            datetime.now(pytz.utc) - startTime,
        )

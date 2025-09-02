import logging
from typing import Union

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.client.controller.LookupCacheController import (
    LookupCacheController,
)

logger = logging.getLogger(__name__)


class ClientLookupTupleProvider(TuplesProviderABC):
    def __init__(self, lookupCacheController: LookupCacheController):
        self._lookupCacheController = lookupCacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        return self._lookupCacheController.cachedVortexMsgBlocking(
            lookupTupleType=tupleSelector.name, filt=filt
        )

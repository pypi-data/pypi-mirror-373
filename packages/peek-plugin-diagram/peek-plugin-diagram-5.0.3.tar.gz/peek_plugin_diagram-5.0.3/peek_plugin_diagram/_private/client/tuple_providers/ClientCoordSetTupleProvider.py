import logging
from typing import Union

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.client.controller.CoordSetCacheController import (
    CoordSetCacheController,
)

logger = logging.getLogger(__name__)


class ClientCoordSetTupleProvider(TuplesProviderABC):
    def __init__(self, coordSetCacheController: CoordSetCacheController):
        self._coordSetCacheController = coordSetCacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        return self._coordSetCacheController.cachedVortexMsgBlocking(filt=filt)

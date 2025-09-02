import logging
from typing import Union

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.client.controller.ModelSetCacheController import (
    ModelSetCacheController,
)

logger = logging.getLogger(__name__)


class ClientModelSetTupleProvider(TuplesProviderABC):
    def __init__(self, modelSetCacheController: ModelSetCacheController):
        self.modelSetCacheController = modelSetCacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        return self.modelSetCacheController.cachedVortexMsgBlocking(filt=filt)

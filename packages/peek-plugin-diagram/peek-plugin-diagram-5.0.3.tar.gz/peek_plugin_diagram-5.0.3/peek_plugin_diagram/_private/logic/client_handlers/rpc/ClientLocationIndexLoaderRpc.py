import logging

from sqlalchemy import select
from vortex.Tuple import Tuple
from vortex.rpc.RPC import vortexRPC

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_plugin_base.PeekVortexUtil import peekBackendNames
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.LocationIndex import (
    LocationIndexCompiled,
)
from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable
from peek_plugin_diagram._private.tuples.location_index.LocationIndexUpdateDateTuple import (
    LocationIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)


class ClientLocationIndexLoaderRpc(ACIChunkLoadRpcABC):
    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadLocationIndexDelta.start(funcSelf=self)
        yield self.loadLocationIndexes.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=diagramFilt,
        deferToThread=True,
    )
    def loadLocationIndexDelta(self, indexEncodedPayload: bytes) -> bytes:
        return self.ckiChunkIndexDeltaBlocking(
            indexEncodedPayload,
            LocationIndexCompiled,
            LocationIndexUpdateDateTuple,
        )

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=diagramFilt,
        deferToThread=True,
    )
    def loadLocationIndexes(self, chunkKeys: list[str]) -> list[Tuple]:
        """Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        chunkTable = LocationIndexCompiled.__table__
        msTable = ModelSetTable.__table__

        sql = (
            select(
                chunkTable.c.indexBucket,
                chunkTable.c.blobData,
                chunkTable.c.lastUpdate,
                msTable.c.key,
            )
            .select_from(chunkTable.join(msTable))
            .where(chunkTable.c.indexBucket.in_(chunkKeys))
        )

        return self.ckiInitialLoadChunksPayloadBlocking(
            chunkKeys, LocationIndexCompiled, sql
        )

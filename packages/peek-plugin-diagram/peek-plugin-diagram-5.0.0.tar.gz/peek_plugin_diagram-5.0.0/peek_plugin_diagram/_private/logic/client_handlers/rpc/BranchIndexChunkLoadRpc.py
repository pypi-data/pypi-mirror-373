import logging

from vortex.Tuple import Tuple
from vortex.rpc.RPC import vortexRPC

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_plugin_base.PeekVortexUtil import peekBackendNames
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import (
    BranchIndexEncodedChunk,
)
from peek_plugin_diagram._private.tuples.branch.BranchIndexUpdateDateTuple import (
    BranchIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)


class BranchIndexChunkLoadRpc(ACIChunkLoadRpcABC):
    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadBranchIndexChunks.start(funcSelf=self)
        yield self.loadBranchIndexDelta.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=diagramFilt,
        deferToThread=True,
    )
    def loadBranchIndexDelta(self, indexEncodedPayload: bytes) -> bytes:
        return self.ckiChunkIndexDeltaBlocking(
            indexEncodedPayload,
            BranchIndexEncodedChunk,
            BranchIndexUpdateDateTuple,
        )

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=diagramFilt,
        deferToThread=True,
    )
    def loadBranchIndexChunks(self, chunkKeys: list[str]) -> list[Tuple]:
        """Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        return self.ckiInitialLoadChunksPayloadBlocking(
            chunkKeys, BranchIndexEncodedChunk
        )

import logging

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.logic.client_handlers.rpc.ClientLocationIndexLoaderRpc import (
    ClientLocationIndexLoaderRpc,
)
from peek_plugin_diagram._private.tuples.location_index.EncodedLocationIndexTuple import (
    EncodedLocationIndexTuple,
)
from peek_plugin_diagram._private.tuples.location_index.LocationIndexUpdateDateTuple import (
    LocationIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientLocationIndexUpdateFromServerFilt = dict(
    key="clientLocationIndexUpdateFromServer"
)
clientLocationIndexUpdateFromServerFilt.update(diagramFilt)


class LocationIndexCacheController(ACICacheControllerABC):
    """Disp Key Cache Controller

    The encodedChunk cache controller stores all the locationIndexs in memory, allowing fast access from
    the mobile and desktop devices.

    """

    _ChunkedTuple = EncodedLocationIndexTuple
    _UpdateDateTupleABC = LocationIndexUpdateDateTuple
    _chunkLoadRpcMethod = ClientLocationIndexLoaderRpc.loadLocationIndexes
    _chunkIndexDeltaRpcMethod = (
        ClientLocationIndexLoaderRpc.loadLocationIndexDelta
    )
    _updateFromLogicFilt = clientLocationIndexUpdateFromServerFilt
    _logger = logger

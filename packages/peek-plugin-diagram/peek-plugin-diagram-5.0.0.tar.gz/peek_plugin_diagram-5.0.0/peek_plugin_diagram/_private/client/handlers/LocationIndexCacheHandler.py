import logging
from typing import Dict

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import (
    clientLocationIndexUpdateFromServerFilt,
)
from peek_plugin_diagram._private.tuples.location_index.LocationIndexUpdateDateTuple import (
    LocationIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientLocationIndexWatchUpdateFromDeviceFilt = {
    "key": "clientLocationIndexWatchUpdateFromDevice"
}
clientLocationIndexWatchUpdateFromDeviceFilt.update(diagramFilt)


# ModelSet HANDLER
class LocationIndexCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = LocationIndexUpdateDateTuple
    _updateFromDeviceFilt: Dict = clientLocationIndexWatchUpdateFromDeviceFilt
    _updateFromLogicFilt: Dict = clientLocationIndexUpdateFromServerFilt
    _logger: logging.Logger = logger

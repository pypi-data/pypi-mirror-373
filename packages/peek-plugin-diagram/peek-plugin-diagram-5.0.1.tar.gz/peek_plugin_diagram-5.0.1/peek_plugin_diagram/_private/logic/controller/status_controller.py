import logging

from peek_abstract_chunked_index.private.server.controller.ACIProcessorStatusControllerABC import (
    ACIProcessorStatusControllerABC,
)
from peek_plugin_diagram._private.tuples.admin.diagram_importer_status_tuple import (
    DiagramProcessingStatusTuple,
)

logger = logging.getLogger(__name__)


class StatusController(ACIProcessorStatusControllerABC):
    NOTIFY_PERIOD = 2.0

    _StateTuple = DiagramProcessingStatusTuple

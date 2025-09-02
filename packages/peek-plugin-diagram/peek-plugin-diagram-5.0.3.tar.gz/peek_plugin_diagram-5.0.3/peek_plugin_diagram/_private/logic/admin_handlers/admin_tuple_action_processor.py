from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_base.PeekVortexUtil import peekAdminName
from peek_plugin_diagram._private.PluginNames import diagramActionProcessorName
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.logic.controller.admin_backend_controller import (
    AdminBackendController,
)


def makeAdminTupleActionProcessorHandler(
    adminBackendController: AdminBackendController,
):
    processor = TupleActionProcessor(
        tupleActionProcessorName=diagramActionProcessorName,
        additionalFilt=diagramFilt,
        defaultDelegate=adminBackendController,
        acceptOnlyFromVortex=peekAdminName,
    )
    return processor

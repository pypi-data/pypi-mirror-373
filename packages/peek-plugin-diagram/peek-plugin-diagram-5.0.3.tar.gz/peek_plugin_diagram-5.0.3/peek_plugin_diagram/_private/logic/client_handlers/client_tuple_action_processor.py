from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_base.PeekVortexUtil import peekBackendNames
from peek_plugin_diagram._private.PluginNames import diagramActionProcessorName
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.logic.controller.branch_live_edit_controller import (
    BranchLiveEditController,
)
from peek_plugin_diagram._private.logic.controller.branch_update_controller import (
    BranchUpdateController,
)
from peek_plugin_diagram._private.tuples.branch.BranchLiveEditTupleAction import (
    BranchLiveEditTupleAction,
)
from peek_plugin_diagram._private.tuples.branch.BranchUpdateTupleAction import (
    BranchUpdateTupleAction,
)


def makeClientTupleActionProcessorHandler(
    branchUpdateController: BranchUpdateController,
    branchLiveEditController: BranchLiveEditController,
):
    processor = TupleActionProcessor(
        tupleActionProcessorName=diagramActionProcessorName,
        additionalFilt=diagramFilt,
        defaultDelegate=None,
        acceptOnlyFromVortex=peekBackendNames,
    )

    processor.setDelegate(
        BranchUpdateTupleAction.tupleName(), branchUpdateController
    )

    processor.setDelegate(
        BranchLiveEditTupleAction.tupleName(), branchLiveEditController
    )

    return processor

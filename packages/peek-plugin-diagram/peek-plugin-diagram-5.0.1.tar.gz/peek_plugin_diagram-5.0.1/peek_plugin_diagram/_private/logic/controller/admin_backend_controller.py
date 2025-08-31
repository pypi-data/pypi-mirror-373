import logging

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC

from peek_plugin_diagram._private.logic.controller.disp_compiler_queue_controller import (
    DispCompilerQueueController,
)
from peek_plugin_diagram._private.logic.controller.grid_key_compiler_queue_controller import (
    GridKeyCompilerQueueController,
)
from peek_plugin_diagram._private.tuples.admin.trggger_canvas_shape_compile_result_tuple import (
    TriggerCanvasShapeCompileResultTuple,
)
from peek_plugin_diagram._private.tuples.admin.trggger_canvas_shape_compile_tuple_action import (
    TriggerCanvasShapeCompileTupleAction,
)

logger = logging.getLogger(__name__)


class AdminBackendController(TupleActionProcessorDelegateABC):

    def __init__(
        self,
        dispCompilerQueueController: DispCompilerQueueController,
        gridKeyCompilerQueueController: GridKeyCompilerQueueController,
    ):
        self._dispCompilerQueueController = dispCompilerQueueController
        self._gridKeyCompilerQueueController = gridKeyCompilerQueueController

    @inlineCallbacks
    def processTupleAction(
        self, tupleAction: TupleActionABC, *args, **kwargs
    ) -> Deferred:
        if isinstance(tupleAction, TriggerCanvasShapeCompileTupleAction):
            shapesQueued, gridsDeleted = yield (
                self._dispCompilerQueueController.queueCanvasDispsToCompile(
                    tupleAction.canvasId
                )
            )
            return [
                TriggerCanvasShapeCompileResultTuple(
                    shapesQueued=shapesQueued, gridsDeleted=gridsDeleted
                )
            ]

        raise NotImplementedError(str(tupleAction))

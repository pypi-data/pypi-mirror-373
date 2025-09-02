from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC


class CanvasConfigChangeEvent(TupleChangeEventABC):
    __eventType__ = "CanvasConfigChangeEvent"
    canvasId: int

    def __init__(self, canvasId):
        self.canvasId = canvasId

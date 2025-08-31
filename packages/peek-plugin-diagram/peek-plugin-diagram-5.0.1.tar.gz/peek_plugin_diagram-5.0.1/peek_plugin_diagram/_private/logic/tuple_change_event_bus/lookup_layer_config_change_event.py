from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC


class LookupLayerConfigChangeEvent(TupleChangeEventABC):
    __eventType__ = "LookupLayerConfigChangeEvent"
    modelSetKey: str
    modelSetId: int
    lookupId: int

    def __init__(self, modelSetKey: str, modelSetId: int, lookupId: int):
        self.modelSetKey = modelSetKey
        self.modelSetId = modelSetId
        self.lookupId = lookupId

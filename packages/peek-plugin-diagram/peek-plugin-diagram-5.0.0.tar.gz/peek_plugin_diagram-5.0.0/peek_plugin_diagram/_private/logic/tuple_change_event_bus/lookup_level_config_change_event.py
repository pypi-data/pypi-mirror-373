from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC


class LookupLevelConfigChangeEvent(TupleChangeEventABC):
    __eventType__ = "LookupLevelConfigChangeEvent"
    modelSetKey: str
    coordSetKey: str
    coordSetId: int
    lookupId: int

    def __init__(
        self, modelSetKey: str, coordSetKey: str, coordSetId: int, lookupId: int
    ):
        self.modelSetKey = modelSetKey
        self.coordSetKey = coordSetKey
        self.coordSetId = coordSetId
        self.lookupId = lookupId

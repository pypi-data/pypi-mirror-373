from vortex.event_bus.TupleChangeEventABC import TupleChangeEventABC


class DiagramLookupChangeEvent(TupleChangeEventABC):
    __eventType__ = "DiagramLookupChangeEvent"

    def __init__(
        self,
        modelSetKey: str,
        modelSetId: int,
        coordSetKey: str | None,
        coordSetId: int | None,
        lookupType: str,
    ):
        self.modelSetKey = modelSetKey
        self.modelSetId = modelSetId
        self.coordSetKey = coordSetKey
        self.coordSetId = coordSetId
        self.lookupType = lookupType

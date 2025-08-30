from typing import Dict
from typing import List

from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable


class ModelSetCacheController:
    """Lookup Cache Controller

    This class caches the lookups in each client.

    """

    def __init__(self, tupleObserver: TupleDataObserverClient):
        self._tupleObserver = tupleObserver
        self._tupleObservable = None

        #: This stores the cache of grid data for the clients
        self._cache: Dict[int, ModelSetTable] = {}

        self._vortexMsgCache = None

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def start(self):
        (
            self._tupleObserver.subscribeToTupleSelector(
                TupleSelector(ModelSetTable.tupleName(), {})
            ).subscribe(self._processNewTuples)
        )

    def shutdown(self):
        self._tupleObservable = None
        self._tupleObserver = None
        self._cache = {}
        self._vortexMsgCache = None

    def _processNewTuples(self, tuples):
        if not tuples:
            return

        self._cache = {c.id: c for c in tuples}

        self._vortexMsgCache = None

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(ModelSetTable.tupleName(), {})
        )

    @property
    def modelSets(self) -> List[ModelSetTable]:
        return list(self._cache.values())

    def cachedVortexMsgBlocking(self, filt: dict) -> bytes:
        if self._vortexMsgCache:
            return self._vortexMsgCache

        data = self.modelSets

        # Create the vortex message
        vortexMsg = (
            Payload(filt, tuples=data).makePayloadEnvelope().toVortexMsg()
        )
        self._vortexMsgCache = vortexMsg
        return vortexMsg

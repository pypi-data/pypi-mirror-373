from copy import copy
from typing import List

from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable

lookupCachePayloadFilt = dict(key="client.lookup.update")
lookupCachePayloadFilt.update(diagramFilt)


class LookupCacheController:
    """Lookup Cache Controller

    This class caches the lookups in each client.

    """

    #: This stores the cache of grid data for the clients
    _levelLookups: List[DispLevelTable] = None
    _layerLookups: List[DispLayerTable] = None
    _colorLookups: List[DispColorTable] = None
    _lineStyleLookups: List[DispLineStyleTable] = None
    _textStyleLookups: List[DispTextStyleTable] = None

    def __init__(self, tupleObserver: TupleDataObserverClient):
        self._tupleObserver = tupleObserver
        self._tupleObservable = None
        self._vortexMsgCache: dict[str, bytes] = {}

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def start(self):
        (
            self._tupleObserver.subscribeToTupleSelector(
                TupleSelector(DispLevelTable.tupleType(), {})
            ).subscribe(self._processNewTuples)
        )

        (
            self._tupleObserver.subscribeToTupleSelector(
                TupleSelector(DispLayerTable.tupleType(), {})
            ).subscribe(self._processNewTuples)
        )

        (
            self._tupleObserver.subscribeToTupleSelector(
                TupleSelector(DispColorTable.tupleType(), {})
            ).subscribe(self._processNewTuples)
        )

        (
            self._tupleObserver.subscribeToTupleSelector(
                TupleSelector(DispLineStyleTable.tupleType(), {})
            ).subscribe(self._processNewTuples)
        )

        (
            self._tupleObserver.subscribeToTupleSelector(
                TupleSelector(DispTextStyleTable.tupleType(), {})
            ).subscribe(self._processNewTuples)
        )

    def shutdown(self):
        self._tupleObservable = None
        self._tupleObserver = None

        self._vortexMsgCache = {}

        self._levelLookups = []
        self._layerLookups = []
        self._colorLookups = []
        self._lineStyleLookups = []
        self._textStyleLookups = []

    def _processNewTuples(self, lookupTuples):
        if not lookupTuples:
            return

        firstTupleType = lookupTuples[0].tupleType()
        if DispLevelTable.tupleType() == firstTupleType:
            self._levelLookups = lookupTuples

        elif DispLayerTable.tupleType() == firstTupleType:
            self._layerLookups = lookupTuples

        elif DispColorTable.tupleType() == firstTupleType:
            self._colorLookups = lookupTuples

        elif DispLineStyleTable.tupleType() == firstTupleType:
            self._lineStyleLookups = lookupTuples

        elif DispTextStyleTable.tupleType() == firstTupleType:
            self._textStyleLookups = lookupTuples

        else:
            raise NotImplementedError(
                "Cache not implemented for %s" % firstTupleType
            )

        self._vortexMsgCache.pop(firstTupleType, None)

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(firstTupleType, {})
        )

    def lookups(self, lookupTupleType) -> List:
        if DispLevelTable.tupleType() == lookupTupleType:
            return copy(self._levelLookups)

        if DispLayerTable.tupleType() == lookupTupleType:
            return copy(self._layerLookups)

        if DispColorTable.tupleType() == lookupTupleType:
            return copy(self._colorLookups)

        if DispLineStyleTable.tupleType() == lookupTupleType:
            return copy(self._lineStyleLookups)

        if DispTextStyleTable.tupleType() == lookupTupleType:
            return copy(self._textStyleLookups)

        raise NotImplementedError(
            "Cache not implemented for %s" % lookupTupleType
        )

    def cachedVortexMsgBlocking(
        self, lookupTupleType: str, filt: dict
    ) -> bytes:
        if lookupTupleType in self._vortexMsgCache:
            return self._vortexMsgCache[lookupTupleType]

        data = self.lookups(lookupTupleType=lookupTupleType)

        # Create the vortex message
        vortexMsg = (
            Payload(filt, tuples=data).makePayloadEnvelope().toVortexMsg()
        )
        self._vortexMsgCache[lookupTupleType] = vortexMsg
        return vortexMsg

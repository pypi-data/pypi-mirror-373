import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Tuple import TUPLE_TYPES_BY_NAME

from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_lookup_change_event import (
    DiagramLookupChangeEvent,
)
from peek_plugin_diagram._private.logic.tuple_change_event_bus.diagram_tuple_change_event_bus import (
    plDiagramTupleChangeEventBus,
)
from peek_plugin_diagram._private.lookup_type_maps import (
    lookupTypeImportTupleToTable,
)
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram._private.storage.ModelSet import getOrCreateCoordSet
from peek_plugin_diagram._private.storage.ModelSet import getOrCreateModelSet
from peek_plugin_diagram.tuples.lookups.ImportDispColorTuple import (
    ImportDispColorTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispLayerTuple import (
    ImportDispLayerTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispLevelTuple import (
    ImportDispLevelTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispLineStyleTuple import (
    ImportDispLineStyleTuple,
)
from peek_plugin_diagram.tuples.lookups.ImportDispTextStyleTuple import (
    ImportDispTextStyleTuple,
)

logger = logging.getLogger(__name__)

ORM_TUPLE_MAP: Dict[str, Any] = {
    ImportDispColorTuple.tupleType(): DispColorTable,
    ImportDispLayerTuple.tupleType(): DispLayerTable,
    ImportDispLevelTuple.tupleType(): DispLevelTable,
    ImportDispLineStyleTuple.tupleType(): DispLineStyleTable,
    ImportDispTextStyleTuple.tupleType(): DispTextStyleTable,
}


class LookupImportController:
    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

        self._semaphore = DeferredSemaphore(1)

    def shutdown(self):
        pass

    @inlineCallbacks
    def importLookups(
        self,
        modelSetKey: str,
        coordSetKey: Optional[str],
        lookupTupleType: str,
        lookupTuples: List,
        deleteOthers: bool,
        updateExisting: bool,
    ):
        yield self._semaphore.run(
            self._importInThread,
            modelSetKey,
            coordSetKey,
            lookupTupleType,
            lookupTuples,
            deleteOthers,
            updateExisting,
        )

        return True

    @deferToThreadWrapWithLogger(logger)
    def _importInThread(
        self,
        modelSetKey: str,
        coordSetKey: str,
        tupleType: str,
        tuples,
        deleteOthers: bool,
        updateExisting: bool,
    ):
        changeEvents = []
        LookupType = ORM_TUPLE_MAP[tupleType]

        if LookupType == DispLineStyleTable:
            self._convertLineStyles(tuples)

        itemsByImportHash = {}

        addCount = 0
        updateCount = 0
        deleteCount = 0

        ormSession = self._dbSessionCreator()
        try:
            modelSet = getOrCreateModelSet(ormSession, modelSetKey)
            coordSet = None

            if coordSetKey:
                coordSet = getOrCreateCoordSet(
                    ormSession, modelSetKey, coordSetKey
                )

                all = (
                    ormSession.query(LookupType)
                    .filter(LookupType.coordSetId == coordSet.id)
                    .all()
                )

            else:
                all = (
                    ormSession.query(LookupType)
                    .filter(LookupType.modelSetId == modelSet.id)
                    .all()
                )

            layerTableTuples = []

            def updateFks(lookup):
                if hasattr(lookup, "coordSetId"):
                    assert coordSet
                    lookup.coordSetId = coordSet.id
                else:
                    lookup.modelSetId = modelSet.id

            for lookup in all:
                # Initialise
                itemsByImportHash[lookup.importHash] = lookup

            for lookup in tuples:
                importHash = str(lookup.importHash)

                # If it's an existing item, update it
                if importHash in itemsByImportHash:
                    existing = itemsByImportHash.pop(importHash)

                    if updateExisting:
                        if existing.blockApiUpdate:
                            logger.debug(
                                f"updating existing lookup to {existing.name}"
                                f" is blocked"
                            )
                        else:
                            for fieldName in lookup.tupleFieldNames():
                                setattr(
                                    existing,
                                    fieldName,
                                    getattr(lookup, fieldName),
                                )

                            updateFks(existing)
                            updateCount += 1

                    tableTuple = existing

                # If it's a new item, create it
                else:
                    newTuple = LookupType()

                    for fieldName in lookup.tupleFieldNames():
                        if fieldName in ("id", "coordSetId", "modelSetId"):
                            continue
                        setattr(newTuple, fieldName, getattr(lookup, fieldName))

                    updateFks(newTuple)
                    ormSession.add(newTuple)
                    addCount += 1

                    tableTuple = newTuple

                if tupleType == ImportDispLayerTuple.tupleType():
                    layerTableTuples.append(tableTuple)

                changeEvents.append(
                    DiagramLookupChangeEvent(
                        modelSetKey=modelSet.key,
                        modelSetId=modelSet.id,
                        coordSetKey=coordSet.key if coordSet else None,
                        coordSetId=coordSet.id if coordSet else None,
                        lookupType=tableTuple.LookupTypeE,
                    )
                )

            if deleteOthers:
                for lookup in list(itemsByImportHash.values()):
                    ormSession.delete(lookup)
                    deleteCount += 1

                    changeEvents.append(
                        DiagramLookupChangeEvent(
                            modelSetKey=modelSet.key,
                            modelSetId=modelSet.id,
                            coordSetKey=coordSet.key if coordSet else None,
                            coordSetId=coordSet.id if coordSet else None,
                            lookupType=lookupTypeImportTupleToTable[
                                lookup.tupleType()
                            ],
                        )
                    )

            layerTableTupleByImportHash = {
                layer.importHash: layer for layer in layerTableTuples
            }
            for layer in layerTableTuples:
                if not layer.parentKey:
                    continue

                if layer.parentKey not in layerTableTupleByImportHash:
                    logger.warning(
                        "Layer for parentKey='%s' doesn't exist",
                        layer.parentKey,
                    )
                    continue

                layer.parent = layerTableTupleByImportHash[layer.parentKey]

            try:
                ormSession.commit()

            except Exception as e:
                ormSession.rollback()
                logger.exception(e)
                raise

            logger.debug(
                "Updates for %s received, Added %s, Updated %s, Deleted %s",
                tupleType,
                addCount,
                updateCount,
                deleteCount,
            )

        finally:
            ormSession.close()

        # Filter for unique events
        changeEvents = list(
            {
                (event.modelSetId, event.coordSetId, event.lookupType): event
                for event in changeEvents
            }.values()
        )

        plDiagramTupleChangeEventBus.notifyMany(changeEvents)

    @deferToThreadWrapWithLogger(logger)
    def getLookups(
        self, modelSetKey: str, coordSetKey: Optional[str], tupleType: str
    ):
        LookupType = ORM_TUPLE_MAP[tupleType]

        ormSession = self._dbSessionCreator()
        try:
            modelSet = getOrCreateModelSet(ormSession, modelSetKey)

            if tupleType == ImportDispLevelTuple.tupleType():
                assert coordSetKey, "coordSetKey is required for disp levels"
                coordSet = getOrCreateCoordSet(
                    ormSession, modelSetKey, coordSetKey
                )

                all = (
                    ormSession.query(LookupType)
                    .filter(LookupType.coordSetId == coordSet.id)
                    .all()
                )

            else:
                all = (
                    ormSession.query(LookupType)
                    .filter(LookupType.modelSetId == modelSet.id)
                    .all()
                )

            importTuples = []
            ImportTuple = TUPLE_TYPES_BY_NAME[tupleType]

            for ormTuple in all:
                newTuple = ImportTuple()

                for fieldName in newTuple.tupleFieldNames():
                    if fieldName == "modelSetKey":
                        newTuple.modelSetKey = modelSetKey

                    elif fieldName == "coordSetKey":
                        newTuple.coordSetKey = coordSetKey

                    elif fieldName == "parentKey":
                        if ormTuple.parent:
                            newTuple.parentKey = ormTuple.parent.importHash

                    else:
                        setattr(
                            newTuple, fieldName, getattr(ormTuple, fieldName)
                        )

                importTuples.append(newTuple)

            return importTuples

        finally:
            ormSession.close()

    def _convertLineStyles(
        self, importLineStyles: List[ImportDispTextStyleTuple]
    ):
        for style in importLineStyles:
            dp = style.dashPattern

            if dp is None:
                continue

            if not isinstance(dp, list):
                dp = [dp]

            style.dashPattern = json.dumps(dp)

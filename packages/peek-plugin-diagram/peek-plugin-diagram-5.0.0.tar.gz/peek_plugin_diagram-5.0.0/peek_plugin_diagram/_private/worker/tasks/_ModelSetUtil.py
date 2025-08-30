import logging
import typing
from collections import defaultdict
from typing import Dict
from typing import List

from sqlalchemy import select

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_diagram._private.storage.ModelSet import (
    ModelSetTable,
    ModelCoordSetTable,
)

logger = logging.getLogger(__name__)

_modelSetTable = ModelSetTable.__table__
_coordSetTable = ModelCoordSetTable.__table__


def getModelSetIdCoordSetId(
    modelSetKeyCoordSetKey: List[typing.Tuple[str, str]]
) -> Dict[typing.Tuple[str, str], typing.Tuple[int, int]]:
    """Get Coord Set Ids

    Given a tuple of (ModelSet.key, CoordSet.key), return with that as the key
    and the CoordSet.id as the value

    """

    results: Dict[typing.Tuple[str, str], typing.Tuple[int, int]] = {}

    coordSetKeysByModelSetKey = defaultdict(list)
    for modelSetKey, coordSetKey in modelSetKeyCoordSetKey:
        coordSetKeysByModelSetKey[modelSetKey].append(coordSetKey)

    modelSetIdByKey = _loadModelSets()

    for modelSetKey, coordSetKeys in coordSetKeysByModelSetKey.items():
        modelSetId = modelSetIdByKey.get(modelSetKey)
        if modelSetId is None:
            modelSetId = _makeModelSet(modelSetKey)
            modelSetIdByKey[modelSetKey] = modelSetId

        coordSetIdByKey = _loadCoordSets(modelSetId)

        for coordSetKey in coordSetKeys:
            coordSetId = modelSetIdByKey.get(coordSetKey)
            if coordSetId is None:
                coordSetId = _makeCoordSet(modelSetId, coordSetKey)
                coordSetIdByKey[coordSetKey] = coordSetId

            results[(modelSetKey, coordSetKey)] = (modelSetId, coordSetId)

    return results


def _loadModelSets() -> Dict[str, int]:
    # Get the model set
    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    try:
        results = list(
            conn.execute(select(_modelSetTable.c.id, _modelSetTable.c.key))
        )
        modelSetIdByKey = {o.key: o.id for o in results}
        del results

    finally:
        conn.close()
    return modelSetIdByKey


def _makeModelSet(modelSetKey: str) -> int:
    # Get the model set
    dbSession = TaskDbConn.getDbSession()
    try:
        newItem = ModelSetTable(key=modelSetKey, name=modelSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()


def _loadCoordSets(modelSetId: int) -> Dict[str, int]:
    # Get the model set
    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    try:
        results = list(
            conn.execute(
                select(_coordSetTable.c.id, _coordSetTable.c.key).where(
                    _coordSetTable.c.modelSetId == modelSetId
                )
            )
        )
        coordSetIdByKey = {o.key: o.id for o in results}
        del results

    finally:
        conn.close()

    return coordSetIdByKey


def _makeCoordSet(modelSetId: int, coordSetKey: str) -> int:
    # Make a coord set
    dbSession = TaskDbConn.getDbSession()
    try:
        maxCoordSetOrder = list(dbSession.query(ModelCoordSetTable.order).all())
        if maxCoordSetOrder:
            newOrder = maxCoordSetOrder[0][0] + 10
        else:
            newOrder = 10

        newItem = ModelCoordSetTable(
            modelSetId=modelSetId,
            key=coordSetKey,
            name=coordSetKey,
            order=newOrder,
        )
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()

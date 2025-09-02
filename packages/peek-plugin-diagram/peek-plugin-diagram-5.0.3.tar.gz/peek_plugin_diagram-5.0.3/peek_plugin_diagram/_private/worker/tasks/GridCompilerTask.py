import hashlib
import logging
from _collections import defaultdict
from base64 import b64encode
from collections import namedtuple
from datetime import datetime
from functools import cmp_to_key
from typing import List

import pytz
from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.GridKeyIndex import (
    GridKeyIndexCompiled,
    GridKeyCompilerQueue,
    GridKeyIndex,
)
from peek_plugin_diagram._private.tuples.grid.GridTuple import GridTuple

from vortex.Payload import Payload

logger = logging.getLogger(__name__)

DispData = namedtuple(
    "DispData",
    [
        "json",
        "id",
        "zOrder",
        "type",
        "levelOrder",
        "levelId",
        "layerOrder",
        "layerId",
    ],
)

""" Grid Compiler

Compile the disp items into the grid data

1) Query for queue
2) Process queue
3) Delete from queue
"""


class NotAllDispsCompiledException(Exception):
    pass


@addPeekWorkerTask(retries=2)
def compileGrids(payloadEncodedArgs: bytes) -> dict[str, str]:
    """Compile Grids Task


    :param payloadEncodedArgs: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    argData = Payload().fromEncodedPayload(payloadEncodedArgs).tuples
    queueItems = argData[0]
    queueItemIds: List[int] = argData[1]

    gridKeys = list(set([i.gridKey for i in queueItems]))
    coordSetIdByGridKey = {i.gridKey: i.coordSetId for i in queueItems}

    lastUpdateByChunkKey = {}

    queueTable = GridKeyCompilerQueue.__table__
    gridTable = GridKeyIndexCompiled.__table__

    startTime = datetime.now(pytz.utc)

    session = TaskDbConn.getDbSession()
    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()
    try:
        logger.debug(
            "Staring compile of %s queueItems in %s",
            len(queueItems),
            (datetime.now(pytz.utc) - startTime),
        )

        total = 0
        dispData = _qryDispData(session, gridKeys)

        conn.execute(
            gridTable.delete().where(gridTable.c.gridKey.in_(gridKeys))
        )

        inserts = []
        for gridKey, dispJsonStr in dispData.items():
            m = hashlib.sha256()
            m.update(gridKey.encode())
            m.update(dispJsonStr.encode())
            gridTupleHash = b64encode(m.digest()).decode()

            lastUpdateByChunkKey[str(gridKey)] = gridTupleHash

            gridTuple = GridTuple(
                gridKey=gridKey,
                dispJsonStr=dispJsonStr,
                lastUpdate=gridTupleHash,
            )

            encodedGridTuple = (
                Payload(tuples=[gridTuple]).toEncodedPayload().encode()
            )

            inserts.append(
                dict(
                    coordSetId=coordSetIdByGridKey[gridKey],
                    gridKey=gridKey,
                    lastUpdate=gridTupleHash,
                    encodedGridTuple=encodedGridTuple,
                )
            )

        if inserts:
            conn.execute(gridTable.insert(), inserts)

        logger.debug(
            "Compiled %s gridKeyTuples, %s missing, in %s",
            len(inserts),
            len(gridKeys) - len(inserts),
            (datetime.now(pytz.utc) - startTime),
        )

        total += len(inserts)

        conn.execute(
            queueTable.delete().where(queueTable.c.id.in_(queueItemIds))
        )

        transaction.commit()
        logger.info(
            "Compiled and Committed %s GridKeyIndexCompileds in %s",
            total,
            (datetime.now(pytz.utc) - startTime),
        )

        return lastUpdateByChunkKey

    except NotAllDispsCompiledException as e:
        logger.warning(
            "Retrying, Not all disps for gridKey %s are compiled", gridKeys
        )
        raise

    except Exception as e:
        transaction.rollback()
        logger.debug("Compile of grids failed, retrying : %s", gridKeys)
        raise

    finally:
        conn.close()
        session.close()


def _dispBaseSortCmp(dispData1, dispData2):
    isData1None = dispData1.levelOrder is None or dispData1.levelOrder is None
    isData2None = dispData2.levelOrder is None or dispData2.levelOrder is None

    if isData1None and isData2None:
        return 0

    elif isData1None:
        return -1

    elif isData2None:
        return 1

    levelOrderDiff = dispData1.levelOrder - dispData2.levelOrder
    if levelOrderDiff != 0:
        return levelOrderDiff

    levelIdDiff = dispData1.levelId - dispData2.levelId
    if levelIdDiff != 0:
        return levelIdDiff

    layerOrderDiff = dispData1.layerOrder - dispData2.layerOrder
    if layerOrderDiff != 0:
        return layerOrderDiff

    layerIdDiff = dispData1.layerId - dispData2.layerId
    if layerIdDiff != 0:
        return layerIdDiff

    if dispData1.zOrder != dispData2.zOrder:
        return dispData1.zOrder - dispData2.zOrder

    return dispData1.type - dispData2.type


def _qryDispData(session, gridKeys):
    indexQry = (
        session.query(
            GridKeyIndex.gridKey,
            DispBase.dispJson,
            DispBase.id,
            DispBase.zOrder,
            DispBase.type,
            DispLevelTable.order,
            DispLevelTable.id,
            DispLayerTable.order,
            DispLayerTable.id,
        )
        .join(DispBase, DispBase.id == GridKeyIndex.dispId)
        .outerjoin(DispLevelTable)
        .outerjoin(DispLayerTable)
        .filter(GridKeyIndex.gridKey.in_(gridKeys))
    )

    dispsByGridKeys = defaultdict(list)
    dispJsonByGridKey = {}

    for item in indexQry:
        dispsByGridKeys[item[0]].append(DispData(*item[1:]))

    for gridKey, dispDatas in list(dispsByGridKeys.items()):
        if list(filter(lambda d: not d.json, dispDatas)):
            raise NotAllDispsCompiledException(
                "Not all disps compiled for %s" % gridKey
            )

        dispsDumpedJson = [
            d.json for d in sorted(dispDatas, key=cmp_to_key(_dispBaseSortCmp))
        ]

        dispJsonByGridKey[gridKey] = "[" + ",".join(dispsDumpedJson) + "]"

    return dispJsonByGridKey

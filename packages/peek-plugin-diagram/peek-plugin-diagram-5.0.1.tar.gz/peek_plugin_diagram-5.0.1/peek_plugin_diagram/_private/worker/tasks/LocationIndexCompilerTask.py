import hashlib
import logging
from _collections import defaultdict
from base64 import b64encode
from datetime import datetime
from typing import List, Dict

import pytz

from vortex.Payload import Payload

from peek_plugin_base.storage.StorageUtil import (
    makeCoreValuesSubqueryCondition,
    makeOrmValuesSubqueryCondition,
)
from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.LocationIndex import (
    LocationIndexCompiled,
    LocationIndex,
)
from peek_plugin_diagram._private.storage.LocationIndex import (
    LocationIndexCompilerQueue,
)
from peek_plugin_diagram._private.storage.ModelSet import ModelSetTable
from peek_plugin_diagram._private.tuples.location_index.LocationIndexTuple import (
    LocationIndexTuple,
)

logger = logging.getLogger(__name__)

""" Location Index Compiler

Compile the location indexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@addPeekWorkerTask(retries=2)
def compileLocationIndex(payloadEncodedArgs: bytes) -> dict[str, str]:
    """Compile Location Index Task


    :param payloadEncodedArgs: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    argData = Payload().fromEncodedPayload(payloadEncodedArgs).tuples
    queueItems = argData[0]
    queueItemIds: List[int] = argData[1]

    indexBuckets = list(set([i.indexBucket for i in queueItems]))
    modelSetIdByIndexBucket = {i.indexBucket: i.modelSetId for i in queueItems}

    queueTable = LocationIndexCompilerQueue.__table__
    compiledTable = LocationIndexCompiled.__table__
    lastUpdate = datetime.now(pytz.utc).isoformat()

    lastUpdateByChunkKey = {}

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

        # Get Model Sets

        modelSetIds = list(set(modelSetIdByIndexBucket.values()))
        modelSetQry = session.query(ModelSetTable.key, ModelSetTable.id).filter(
            ModelSetTable.id.in_(modelSetIds)
        )

        modelSetKeyByModelSetId = {o.id: o.key for o in modelSetQry}

        total = 0
        dispData = _buildIndex(session, indexBuckets)

        conn.execute(
            compiledTable.delete().where(
                makeCoreValuesSubqueryCondition(
                    engine, compiledTable.c.indexBucket, indexBuckets
                )
            )
        )
        transaction.commit()
        transaction = conn.begin()

        inserts = []
        for indexBucket, jsonStr in dispData.items():
            modelSetId = modelSetIdByIndexBucket[indexBucket]
            modelSetKey = modelSetKeyByModelSetId[modelSetId]

            m = hashlib.sha256()
            m.update(modelSetKey.encode())
            m.update(jsonStr.encode())
            dataHash = b64encode(m.digest()).decode()

            lastUpdateByChunkKey[str(indexBucket)] = dataHash

            locationIndexTuple = LocationIndexTuple(
                modelSetKey=modelSetKey,
                indexBucket=indexBucket,
                jsonStr=jsonStr,
                lastUpdate=dataHash,
            )

            blobData = (
                Payload(tuples=[locationIndexTuple]).toEncodedPayload().encode()
            )

            inserts.append(
                dict(
                    modelSetId=modelSetId,
                    indexBucket=indexBucket,
                    lastUpdate=dataHash,
                    blobData=blobData,
                )
            )

        if inserts:
            conn.execute(compiledTable.insert(), inserts)

        logger.debug(
            "Compiled %s LocationIndexes, %s missing, in %s",
            len(inserts),
            len(indexBuckets) - len(inserts),
            (datetime.now(pytz.utc) - startTime),
        )

        total += len(inserts)

        conn.execute(
            queueTable.delete().where(
                makeCoreValuesSubqueryCondition(
                    engine, queueTable.c.id, queueItemIds
                )
            )
        )

        transaction.commit()
        logger.info(
            "Compiled and Comitted %s LocationIndexCompileds in %s",
            total,
            (datetime.now(pytz.utc) - startTime),
        )

        return lastUpdateByChunkKey

    except Exception as e:
        transaction.rollback()
        # logger.warning(e)  # Just a warning, it will retry
        logger.exception(e)
        raise

    finally:
        conn.close()
        session.close()


def _buildIndex(session, indexBuckets) -> Dict[str, str]:
    indexQry = (
        session.query(
            LocationIndex.indexBucket,
            DispBase.id,
            DispBase.key,
            DispBase.locationJson,
        )
        .join(DispBase, DispBase.id == LocationIndex.dispId)
        .filter(
            makeOrmValuesSubqueryCondition(
                session, LocationIndex.indexBucket, indexBuckets
            )
        )
        .order_by(DispBase.key, DispBase.id)
    )

    jsonByIndexBucket = {}

    # Create the IndexBucket -> Key -> [Locations] structure
    locationByKeyByBucket = defaultdict(lambda: defaultdict(list))
    for item in indexQry:
        locationByKeyByBucket[item.indexBucket][item.key].append(
            item.locationJson
        )

    # Sort each bucket by the key
    for indexBucket, locationByKey in locationByKeyByBucket.items():
        # Create a list of of key, [locationJson, locationJson, locationJson]
        sortedKeyLocations = list(
            sorted(locationByKey.items(), key=lambda i: i[0])
        )

        # [even] is a key, [odd] is the locations json string
        indexStructure = []
        for key, locationsJson in sortedKeyLocations:
            # Combine the key and locations into one json array
            indexStructure.append(
                '["%s",' % key + ",".join(locationsJson) + "]"
            )

        # Create the blob data for this index.
        # It will be searched by a binary sort
        jsonByIndexBucket[indexBucket] = "[" + ",".join(indexStructure) + "]"

    return jsonByIndexBucket

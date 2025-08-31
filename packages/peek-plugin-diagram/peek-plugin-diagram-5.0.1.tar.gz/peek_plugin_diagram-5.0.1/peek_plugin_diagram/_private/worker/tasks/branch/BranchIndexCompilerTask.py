import hashlib
import logging
from base64 import b64encode
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
import json
from sqlalchemy import select

from vortex.Payload import Payload

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.storage.branch.BranchIndexCompilerQueue import (
    BranchIndexCompilerQueue,
)
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import (
    BranchIndexEncodedChunk,
)

logger = logging.getLogger(__name__)

""" BranchIndex Index Compiler

Compile the index-blueprintindexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@addPeekWorkerTask(retries=10)
def compileBranchIndexChunk(payloadEncodedArgs: bytes) -> dict[str, str]:
    """Compile BranchIndex Index Task

    :param payloadEncodedArgs: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    argData = Payload().fromEncodedPayload(payloadEncodedArgs).tuples
    queueItems = argData[0]
    queueItemIds: List[int] = argData[1]

    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()
    try:
        queueItemsByModelSetId = defaultdict(list)

        for queueItem in queueItems:
            queueItemsByModelSetId[queueItem.modelSetId].append(queueItem)

        lastUpdateByChunkKey = {}
        for modelSetId, modelSetQueueItems in queueItemsByModelSetId.items():
            lastUpdateByChunkKey.update(
                _compileBranchIndexChunk(
                    conn, transaction, modelSetId, modelSetQueueItems
                )
            )

        queueTable = BranchIndexCompilerQueue.__table__

        transaction = conn.begin()
        conn.execute(
            queueTable.delete().where(queueTable.c.id.in_(queueItemIds))
        )
        transaction.commit()

    except Exception as e:
        transaction.rollback()
        logger.debug("RETRYING task - %s", e)
        raise

    finally:
        conn.close()

    return lastUpdateByChunkKey


def _compileBranchIndexChunk(
    conn,
    transaction,
    modelSetId: int,
    queueItems: List[BranchIndexCompilerQueue],
) -> dict[str, str]:
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    compiledTable = BranchIndexEncodedChunk.__table__
    lastUpdate = datetime.now(pytz.utc).isoformat()

    startTime = datetime.now(pytz.utc)

    logger.debug(
        "Staring compile of %s queueItems in %s",
        len(queueItems),
        (datetime.now(pytz.utc) - startTime),
    )

    # Get Model Sets

    total = 0
    existingHashes = _loadExistingHashes(conn, chunkKeys)
    encKwPayloadByChunkKey = _buildIndex(chunkKeys)
    chunksToDelete = []

    lastUpdateByChunkKey = {}

    inserts = []
    for (
        chunkKey,
        diagramIndexChunkEncodedPayload,
    ) in encKwPayloadByChunkKey.items():
        m = hashlib.sha256()
        m.update(diagramIndexChunkEncodedPayload.encode())
        encodedHash = b64encode(m.digest()).decode()

        # Compare the hash, AND delete the chunk key
        if chunkKey in existingHashes:
            # At this point we could decide to do an update instead,
            # but inserts are quicker
            if encodedHash == existingHashes.pop(chunkKey):
                continue

        lastUpdateByChunkKey[chunkKey] = lastUpdate

        chunksToDelete.append(chunkKey)
        inserts.append(
            dict(
                modelSetId=modelSetId,
                chunkKey=chunkKey,
                encodedData=diagramIndexChunkEncodedPayload.encode(),
                encodedHash=encodedHash,
                lastUpdate=lastUpdate,
            )
        )

    # Add any chnuks that we need to delete that we don't have new data for, here
    chunksToDelete.extend(list(existingHashes))

    if chunksToDelete:
        # Delete the old chunks
        conn.execute(
            compiledTable.delete().where(
                compiledTable.c.chunkKey.in_(chunksToDelete)
            )
        )

    if inserts:
        newIdGen = TaskDbConn.prefetchDeclarativeIds(BranchIndex, len(inserts))
        for insert in inserts:
            insert["id"] = next(newIdGen)

    transaction.commit()
    transaction = conn.begin()

    if inserts:
        conn.execute(compiledTable.insert(), inserts)

    logger.debug(
        "Compiled %s BranchIndexs, %s missing, in %s",
        len(inserts),
        len(chunkKeys) - len(inserts),
        (datetime.now(pytz.utc) - startTime),
    )

    total += len(inserts)

    transaction.commit()
    logger.debug(
        "Compiled and Committed %s EncodedBranchIndexChunks in %s",
        total,
        (datetime.now(pytz.utc) - startTime),
    )

    return lastUpdateByChunkKey


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = BranchIndexEncodedChunk.__table__

    results = conn.execute(
        select(compiledTable.c.chunkKey, compiledTable.c.encodedHash).where(
            compiledTable.c.chunkKey.in_(chunkKeys)
        )
    ).fetchall()

    return {result[0]: result[1] for result in results}


def _buildIndex(chunkKeys) -> Dict[str, bytes]:
    session = TaskDbConn.getDbSession()

    try:
        indexQry = (
            session.query(
                BranchIndex.chunkKey, BranchIndex.key, BranchIndex.packedJson
            )
            .filter(BranchIndex.chunkKey.in_(chunkKeys))
            .order_by(BranchIndex.key)
            .yield_per(1000)
            .all()
        )

        # Create the ChunkKey -> {key -> packedJson, key -> packedJson, ....]
        packagedJsonsByObjKeyByChunkKey = defaultdict(lambda: defaultdict(list))

        for item in indexQry:
            packagedJsonsByObjKeyByChunkKey[item.chunkKey][item.key].append(
                item.packedJson
            )

        encPayloadByChunkKey = {}

        # Sort each bucket by the key
        for (
            chunkKey,
            packedJsonsByKey,
        ) in packagedJsonsByObjKeyByChunkKey.items():
            tuples = json.dumps(packedJsonsByKey, sort_keys=True)

            # Create the blob data for this index.
            # It will be index-blueprint by a binary sort
            encPayloadByChunkKey[chunkKey] = Payload(
                tuples=tuples
            ).toEncodedPayload()

        return encPayloadByChunkKey

    finally:
        session.close()

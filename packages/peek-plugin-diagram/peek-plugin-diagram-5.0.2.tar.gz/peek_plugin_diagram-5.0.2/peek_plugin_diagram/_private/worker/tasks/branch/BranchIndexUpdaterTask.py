import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Set, Tuple, Dict

import pytz
from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_diagram._private.logic.controller.disp_compiler_queue_controller import (
    DispCompilerQueueController,
)
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.GridKeyIndex import (
    GridKeyIndex,
    GridKeyCompilerQueue,
)
from peek_plugin_diagram._private.storage.ModelSet import (
    ModelCoordSetTable,
    ModelSetTable,
)
from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.storage.branch.BranchIndexCompilerQueue import (
    BranchIndexCompilerQueue,
)
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_diagram._private.worker.tasks.ImportDispTask import (
    _bulkInsertDisps,
)
from peek_plugin_diagram._private.worker.tasks.branch.BranchDispUpdater import (
    _deleteBranchDisps,
    _convertBranchDisps,
)
from peek_plugin_diagram._private.worker.tasks.branch._BranchIndexCalcChunkKey import (
    makeChunkKeyForBranchIndex,
)
from sqlalchemy import select, and_, bindparam
from sqlalchemy.orm.exc import NoResultFound

from vortex.Payload import Payload

logger = logging.getLogger(__name__)


@addPeekWorkerTask(retries=3)
def updateBranches(modelSetId: int, branchEncodedPayload: bytes) -> None:
    """Update Branch

    This method is called from the UI to update a single branch.
    It could be called from a server API as well.

    All the branches must be for the same model set.

    """
    # Decode BranchTuples payload
    updatedBranches: List[BranchTuple] = (
        Payload().fromEncodedPayload(branchEncodedPayload).tuples
    )

    startTime = datetime.now(pytz.utc)

    queueTable = BranchIndexCompilerQueue.__table__
    dispBaseTable = DispBase.__table__
    gridKeyIndexTable = GridKeyIndex.__table__

    gridKeyCompilerQueueTable = GridKeyCompilerQueue.__table__

    branchesByCoordSetId: Dict[int, List[BranchTuple]] = defaultdict(list)
    chunkKeys: Set[str] = set()

    newBranchesToInsert = []

    # Create a lookup of CoordSets by ID
    dbSession = TaskDbConn.getDbSession()
    try:
        # Get the latest lookups
        modelSet = (
            dbSession.query(ModelSetTable)
            .filter(ModelSetTable.id == modelSetId)
            .one()
        )
        coordSetById = {
            i.id: i for i in dbSession.query(ModelCoordSetTable).all()
        }
        dbSession.expunge_all()

        # Update the branches
        # This will be a performance problem if lots of branches are updated,
        # however, on first writing this will just be used by the UI for updating
        # individual branches.
        for branch in updatedBranches:
            try:
                if str(branch.id).startswith("NEW_"):
                    branch.id = None

                if branch.id is None:
                    branchIndex = (
                        dbSession.query(BranchIndex)
                        .filter(BranchIndex.coordSetId == branch.coordSetId)
                        .filter(BranchIndex.key == branch.key)
                        .one()
                    )
                else:
                    branchIndex = (
                        dbSession.query(BranchIndex)
                        .filter(BranchIndex.id == branch.id)
                        .one()
                    )
                branch.id = branchIndex.id
                branchIndex.packedJson = branch.packJson()
                branchIndex.updatedDate = branch.updatedDate

            except NoResultFound:
                newBranchesToInsert.append(branch)

            branchesByCoordSetId[branch.coordSetId].append(branch)

            chunkKeys.add(makeChunkKeyForBranchIndex(modelSet.key, branch.key))

        dbSession.commit()

    except Exception as e:
        dbSession.rollback()
        logger.debug("Retrying updateBranch, %s", e)
        logger.exception(e)
        raise

    finally:
        dbSession.close()

    dbSession = TaskDbConn.getDbSession()

    try:
        if newBranchesToInsert:
            _insertOrUpdateBranches(
                dbSession, modelSet.key, modelSet.id, newBranchesToInsert
            )
            dbSession.commit()

        # Make an array of all branch IDs
        allBranchIds = []
        for branches in branchesByCoordSetId.values():
            allBranchIds.extend([b.id for b in branches])

        # Find out all the existing grids effected by this branch.
        gridsToRecompile = dbSession.execute(
            select(gridKeyIndexTable.c.gridKey, gridKeyIndexTable.c.coordSetId)
            .select_from(gridKeyIndexTable.join(dispBaseTable))
            .where(dispBaseTable.c.branchId.in_(allBranchIds))
            .distinct()
        ).fetchall()

        allNewDisps = []
        allDispIdsToCompile = []

        packedJsonUpdates = []
        # Recompile the BranchGridIndexes
        for coordSetId, branches in branchesByCoordSetId.items():
            coordSet = coordSetById[coordSetId]
            assert (
                coordSet.modelSetId == modelSetId
            ), "Branches not all from one model"

            newDisps, dispIdsToCompile = _convertBranchDisps(branches)
            allNewDisps.extend(newDisps)
            allDispIdsToCompile.extend(dispIdsToCompile)

            packedJsonUpdates.extend(
                [dict(b_id=b.id, b_packedJson=b.packJson()) for b in branches]
            )

        dbSession.execute(
            dispBaseTable.delete().where(
                dispBaseTable.c.branchId.in_(allBranchIds)
            )
        )

        dbSession.commit()

        # NO TRANSACTION
        # Bulk load the Disps
        _bulkInsertDisps(TaskDbConn.getDbEngine(), allNewDisps)

        # Queue the compiler
        DispCompilerQueueController.queueDispIdsToCompileWithSession(
            allDispIdsToCompile, dbSession
        )

        # Update the JSON again back into the grid index.
        stmt = (
            BranchIndex.__table__.update()
            .where(BranchIndex.__table__.c.id == bindparam("b_id"))
            .values(packedJson=bindparam("b_packedJson"))
        )
        dbSession.execute(stmt, packedJsonUpdates)

        # 3) Queue chunks for recompile
        dbSession.execute(
            queueTable.insert(),
            [dict(modelSetId=modelSetId, chunkKey=c) for c in chunkKeys],
        )

        # 4) Queue chunks for
        if gridsToRecompile:
            dbSession.execute(
                gridKeyCompilerQueueTable.insert(),
                [
                    dict(coordSetId=item.coordSetId, gridKey=item.gridKey)
                    for item in gridsToRecompile
                ],
            )

        dbSession.commit()

        logger.debug(
            "Updated %s BranchIndexes queued %s chunks in %s",
            len(updatedBranches),
            len(chunkKeys),
            (datetime.now(pytz.utc) - startTime),
        )

    except Exception as e:
        dbSession.rollback()
        logger.debug("Retrying updateBranch, %s", e)
        logger.exception(e)
        raise

    finally:
        dbSession.close()


@addPeekWorkerTask(retries=3)
def removeBranches(modelSetKey: str, coordSetKey: str, keys: List[str]) -> None:
    """Remove Branches

    This worker task removes branches from the indexes.

    """

    startTime = datetime.now(pytz.utc)

    branchIndexTable = BranchIndex.__table__
    queueTable = BranchIndexCompilerQueue.__table__

    # Create a lookup of CoordSets by ID
    dbSession = TaskDbConn.getDbSession()
    try:
        coordSet = (
            dbSession.query(ModelCoordSetTable)
            .filter(ModelCoordSetTable.modelSet.key == modelSetKey)
            .filter(ModelCoordSetTable.key == coordSetKey)
            .one()
        )

        dbSession.expunge_all()

    finally:
        dbSession.close()

    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        items = conn.execute(
            select(branchIndexTable.c.id, branchIndexTable.c.chunkKey)
            .where(
                and_(
                    branchIndexTable.c.key.in_(keys),
                    branchIndexTable.c.coordSetId == coordSet.id,
                )
            )
            .distinct()
        ).fetchall()

        branchIndexIds = [i.id for i in items]
        chunkKeys = set([i.chunkKey for i in items])

        _deleteBranchDisps(conn, branchIndexIds)

        # 1) Delete existing branches
        conn.execute(
            branchIndexTable.delete().where(
                branchIndexTable.c.id.in_(branchIndexIds)
            )
        )

        # 3) Queue chunks for recompile
        conn.execute(
            queueTable.insert(),
            [
                dict(modelSetId=coordSet.modelSetId, chunkKey=c)
                for c in chunkKeys
            ],
        )

        transaction.commit()
        logger.debug(
            "Deleted %s BranchIndexes queued %s chunks in %s",
            len(branchIndexIds),
            len(chunkKeys),
            (datetime.now(pytz.utc) - startTime),
        )

    except Exception as e:
        transaction.rollback()
        logger.debug("Retrying createOrUpdateBranches, %s", e)
        logger.exception(e)
        raise

    finally:
        conn.close()


def _insertOrUpdateBranches(
    conn, modelSetKey: str, modelSetId: int, newBranches: List[BranchTuple]
) -> None:
    """Insert or Update Branches

    1) Delete existing branches
    2) Insert new branches
    3) Queue chunks for recompile

    """

    startTime = datetime.now(pytz.utc)

    branchIndexTable = BranchIndex.__table__
    queueTable = BranchIndexCompilerQueue.__table__

    importHashSet = set()

    chunkKeysForQueue: Set[Tuple[int, str]] = set()

    # Get the IDs that we need
    newIdGen = TaskDbConn.prefetchDeclarativeIds(BranchIndex, len(newBranches))

    # Create state arrays
    inserts = []

    # Work out which objects have been updated or need inserting
    for newBranch in newBranches:
        importHashSet.add(newBranch.importGroupHash)

        # noinspection PyTypeChecker
        newBranch.id = next(newIdGen)
        branchJson = newBranch.packJson()

        existingObject = BranchIndex(
            id=newBranch.id,
            coordSetId=newBranch.coordSetId,
            key=newBranch.key,
            updatedDate=newBranch.updatedDate,
            createdDate=newBranch.createdDate,
            importHash=newBranch.importHash,
            importGroupHash=newBranch.importGroupHash,
            chunkKey=makeChunkKeyForBranchIndex(modelSetKey, newBranch.key),
            packedJson=branchJson,
        )
        inserts.append(existingObject.tupleToSqlaBulkInsertDict())

        chunkKeysForQueue.add((modelSetId, existingObject.chunkKey))

    # 1) Delete existing branches
    if importHashSet:
        # Make note of the IDs being deleted
        # FIXME : Unused
        branchIndexIdsBeingDeleted = [
            item.id
            for item in conn.execute(
                select(branchIndexTable.c.id)
                .where(branchIndexTable.c.importGroupHash.in_(importHashSet))
                .distinct()
            )
        ]

        conn.execute(
            branchIndexTable.delete().where(
                branchIndexTable.c.importGroupHash.in_(importHashSet)
            )
        )

    # 2) Insert new branches
    if inserts:
        conn.execute(branchIndexTable.insert(), inserts)

    # 3) Queue chunks for recompile
    if chunkKeysForQueue:
        conn.execute(
            queueTable.insert(),
            [dict(modelSetId=m, chunkKey=c) for m, c in chunkKeysForQueue],
        )

    logger.debug(
        "Inserted %s queued %s chunks in %s",
        len(inserts),
        len(chunkKeysForQueue),
        (datetime.now(pytz.utc) - startTime),
    )

import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional

import pytz
from sqlalchemy import select, and_

from vortex.Payload import Payload

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_graphdb._private.storage.GraphDbCompilerQueue import (
    GraphDbCompilerQueue,
)
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment
from peek_plugin_graphdb._private.tuples.ItemKeyTuple import ItemKeyTuple
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_graphdb._private.worker.tasks.ItemKeyIndexImporterTask import (
    ItemKeyImportTuple,
    loadItemKeys,
    deleteItemKeys,
)
from peek_plugin_graphdb._private.worker.tasks._SegmentIndexCalcChunkKey import (
    makeChunkKeyForSegmentKey,
)
from peek_plugin_graphdb.tuples.GraphDbImportSegmentTuple import (
    GraphDbImportSegmentTuple,
)

logger = logging.getLogger(__name__)


@addPeekWorkerTask()
def deleteSegment(
    modelSetKey: str,
    importGroupHashes: List[str],
    segmentKeys: Optional[List[str]] = None,
) -> None:
    if not segmentKeys:
        segmentKeys = []

    startTime = datetime.now(pytz.utc)

    segmentTable = GraphDbSegment.__table__
    queueTable = GraphDbCompilerQueue.__table__

    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        modelSetIdByKey = _loadModelSets()
        modelSetId = modelSetIdByKey[modelSetKey]

        chunkKeys = []

        if importGroupHashes:
            chunkKeys += [
                dict(modelSetId=row[0], chunkKey=row[1])
                for row in conn.execute(
                    select(
                        segmentTable.c.modelSetId, segmentTable.c.chunkKey
                    ).where(
                        and_(
                            segmentTable.c.importGroupHash.in_(
                                importGroupHashes
                            ),
                            segmentTable.c.modelSetId == modelSetId,
                        )
                    )
                ).fetchall()
            ]

            conn.execute(
                segmentTable.delete().where(
                    and_(
                        segmentTable.c.importGroupHash.in_(importGroupHashes),
                        segmentTable.c.modelSetId == modelSetId,
                    )
                )
            )

        if segmentKeys:
            chunkKeys += [
                dict(modelSetId=row[0], chunkKey=row[1])
                for row in conn.execute(
                    select(
                        segmentTable.c.modelSetId, segmentTable.c.chunkKey
                    ).where(
                        and_(
                            segmentTable.c.key.in_(segmentKeys),
                            segmentTable.c.modelSetId == modelSetId,
                        )
                    )
                ).fetchall()
            ]

            conn.execute(
                segmentTable.delete().where(
                    and_(
                        segmentTable.c.key.in_(segmentKeys),
                        segmentTable.c.modelSetId == modelSetId,
                    )
                )
            )

        if chunkKeys:
            conn.execute(queueTable.insert(), chunkKeys)

        deleteItemKeys(conn, modelSetId, importGroupHashes)

        transaction.commit()

        logger.info(
            "Deleted %s by importGroupHas, %s by segmentKey,"
            " queued %s chunks in %s",
            len(importGroupHashes),
            len(segmentKeys),
            len(chunkKeys),
            (datetime.now(pytz.utc) - startTime),
        )

    except Exception as e:
        transaction.rollback()
        logger.debug("Retrying graphDb deleteSegment, %s", e)
        raise

    finally:
        conn.close()


@addPeekWorkerTask()
def createOrUpdateSegments(segmentEncodedPayload: bytes) -> None:
    # Decode arguments
    newSegments: List[GraphDbImportSegmentTuple] = (
        Payload().fromEncodedPayload(segmentEncodedPayload).tuples
    )

    _validateNewSegments(newSegments)

    modelSetIdByKey = _loadModelSets()

    # Do the import
    try:
        segmentByModelKey = defaultdict(list)
        for segment in newSegments:
            segmentByModelKey[segment.modelSetKey].append(segment)

        for modelSetKey, segments in segmentByModelKey.items():
            modelSetId = modelSetIdByKey.get(modelSetKey)
            if modelSetId is None:
                modelSetId = _makeModelSet(modelSetKey)
                modelSetIdByKey[modelSetKey] = modelSetId

            _insertOrUpdateObjects(segments, modelSetId, modelSetKey)

    except Exception as e:
        logger.debug("Retrying import graphDb objects, %s", e)
        raise


def _validateNewSegments(newSegments: List[GraphDbImportSegmentTuple]) -> None:
    for segment in newSegments:
        if not segment.key:
            raise Exception("key is empty for %s" % segment)

        if not segment.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % segment)


def _loadModelSets() -> Dict[str, int]:
    # Get the model set
    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    try:
        modelSetTable = GraphDbModelSet.__table__
        results = list(
            conn.execute(select(modelSetTable.c.id, modelSetTable.c.key))
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
        newItem = GraphDbModelSet(key=modelSetKey, name=modelSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()


def _insertOrUpdateObjects(
    newSegments: List[GraphDbImportSegmentTuple],
    modelSetId: int,
    modelSetKey: str,
) -> None:
    """Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    segmentTable = GraphDbSegment.__table__
    queueTable = GraphDbCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)
    importHashSet = set()

    chunkKeysForQueue: Set[Tuple[int, str]] = set()

    # Get the IDs that we need
    newIdGen = TaskDbConn.prefetchDeclarativeIds(
        GraphDbSegment, len(newSegments)
    )

    # Create state arrays
    inserts = []

    newItemKeys = []

    # Work out which objects have been updated or need inserting
    for importSegment in newSegments:
        importHashSet.add(importSegment.importGroupHash)
        segmentJson = importSegment.packJson()

        id_ = next(newIdGen)
        existingObject = GraphDbSegment(
            id=id_,
            modelSetId=modelSetId,
            key=importSegment.key,
            importGroupHash=importSegment.importGroupHash,
            chunkKey=makeChunkKeyForSegmentKey(
                importSegment.modelSetKey, importSegment.key
            ),
            segmentJson=segmentJson,
        )
        inserts.append(existingObject.tupleToSqlaBulkInsertDict())

        chunkKeysForQueue.add((modelSetId, existingObject.chunkKey))

        for edge in importSegment.edges:
            newItemKeys.append(
                ItemKeyImportTuple(
                    importGroupHash=importSegment.importGroupHash,
                    itemKey=edge.key,
                    itemType=ItemKeyTuple.ITEM_TYPE_EDGE,
                    segmentKey=importSegment.key,
                )
            )

        for vertex in importSegment.vertexes:
            newItemKeys.append(
                ItemKeyImportTuple(
                    importGroupHash=importSegment.importGroupHash,
                    itemKey=vertex.key,
                    itemType=ItemKeyTuple.ITEM_TYPE_VERTEX,
                    segmentKey=importSegment.key,
                )
            )

    # TODO: If this fails, we could potentially delete by segment key.
    # But that seems a bit hackish, the agents should delete the old first.
    # Or should they. That might leave a temporary gap in the network.

    # Delete old stuff
    if importHashSet:
        deleteSegment(
            modelSetKey=modelSetKey, importGroupHashes=list(importHashSet)
        )

    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        # Insert the GraphDb Objects
        if inserts:
            conn.execute(segmentTable.insert(), inserts)

        if chunkKeysForQueue:
            conn.execute(
                queueTable.insert(),
                [dict(modelSetId=m, chunkKey=c) for m, c in chunkKeysForQueue],
            )

        loadItemKeys(conn, newItemKeys, modelSetId, modelSetKey)

        if inserts or chunkKeysForQueue or newItemKeys:
            transaction.commit()
        else:
            transaction.rollback()

        logger.info(
            "Inserted %s queued %s chunks in %s",
            len(inserts),
            len(chunkKeysForQueue),
            (datetime.now(pytz.utc) - startTime),
        )

    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()

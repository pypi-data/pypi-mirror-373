import hashlib
import json
import logging
from base64 import b64encode
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
from sqlalchemy import select

from vortex.Payload import Payload

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_graphdb._private.storage.GraphDbCompilerQueue import (
    GraphDbCompilerQueue,
)
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import (
    GraphDbEncodedChunk,
)
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment

logger = logging.getLogger(__name__)

""" GraphDb Index Compiler

Compile the graphDb indexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@addPeekWorkerTask()
def compileSegmentChunk(payloadEncodedArgs: bytes) -> dict[str, str]:
    """Compile GraphDb Index Task


    :param payloadEncodedArgs: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    argData = Payload().fromEncodedPayload(payloadEncodedArgs).tuples
    queueItems = argData[0]
    queueItemIds: List[int] = argData[1]

    queueTable = GraphDbCompilerQueue.__table__

    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    try:
        queueItemsByModelSetId = defaultdict(list)

        for queueItem in queueItems:
            queueItemsByModelSetId[queueItem.modelSetId].append(queueItem)

        transaction = conn.begin()
        try:
            lastUpdateByChunkKey = {}
            for (
                modelSetId,
                modelSetQueueItems,
            ) in queueItemsByModelSetId.items():
                lastUpdateByChunkKey.update(
                    _compileSegmentChunk(conn, modelSetId, modelSetQueueItems)
                )

            conn.execute(
                queueTable.delete().where(queueTable.c.id.in_(queueItemIds))
            )
            transaction.commit()
        except:
            transaction.rollback()
            raise

    except Exception as e:
        logger.debug("RETRYING task - %s", e)
        raise

    finally:
        conn.close()

    return lastUpdateByChunkKey


def _compileSegmentChunk(
    conn, modelSetId: int, queueItems: List[GraphDbCompilerQueue]
) -> dict[str, str]:
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    compiledTable = GraphDbEncodedChunk.__table__
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
        graphDbIndexChunkEncodedPayload,
    ) in encKwPayloadByChunkKey.items():
        m = hashlib.sha256()
        m.update(graphDbIndexChunkEncodedPayload)
        encodedHash = b64encode(m.digest()).decode()

        # Compare the hash, AND delete the chunk key
        if chunkKey in existingHashes:
            # At this point we could decide to do an update instead,
            # but inserts are quicker
            if encodedHash == existingHashes.pop(chunkKey):
                continue

        lastUpdateByChunkKey[str(chunkKey)] = lastUpdate

        chunksToDelete.append(chunkKey)
        inserts.append(
            dict(
                modelSetId=modelSetId,
                chunkKey=chunkKey,
                encodedData=graphDbIndexChunkEncodedPayload,
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
        newIdGen = TaskDbConn.prefetchDeclarativeIds(
            GraphDbSegment, len(inserts)
        )
        for insert in inserts:
            insert["id"] = next(newIdGen)

    if inserts:
        conn.execute(compiledTable.insert(), inserts)

    logger.debug(
        "Compiled %s Segments, %s missing, in %s",
        len(inserts),
        len(chunkKeys) - len(inserts),
        (datetime.now(pytz.utc) - startTime),
    )

    total += len(inserts)

    logger.info(
        "Compiled and Committed %s EncodedSegmentChunks in %s",
        total,
        (datetime.now(pytz.utc) - startTime),
    )

    return lastUpdateByChunkKey


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = GraphDbEncodedChunk.__table__

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
                GraphDbSegment.chunkKey,
                GraphDbSegment.key,
                GraphDbSegment.segmentJson,
            )
            .filter(GraphDbSegment.chunkKey.in_(chunkKeys))
            .order_by(GraphDbSegment.key)
            .yield_per(1000)
            .all()
        )

        # Create the ChunkKey -> {id -> packedJson, id -> packedJson, ....]
        packagedJsonByObjIdByChunkKey = defaultdict(dict)

        for item in indexQry:
            packagedJsonByObjIdByChunkKey[item.chunkKey][
                item.key
            ] = item.segmentJson

        encPayloadByChunkKey = {}

        # Sort each bucket by the key
        for chunkKey, packedJsonByKey in packagedJsonByObjIdByChunkKey.items():
            tuples = json.dumps(packedJsonByKey, sort_keys=True)

            # Create the blob data for this index.
            # It will be graphDbed by a binary sort
            encPayloadByChunkKey[chunkKey] = (
                Payload(tuples=tuples).toEncodedPayload().encode()
            )

        return encPayloadByChunkKey

    finally:
        session.close()

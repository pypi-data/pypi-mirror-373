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
from peek_core_docdb._private.storage.DocDbCompilerQueue import (
    DocDbCompilerQueue,
)
from peek_core_docdb._private.storage.DocDbDocument import DocDbDocument
from peek_core_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk

logger = logging.getLogger(__name__)

""" DocDb Index Compiler

Compile the docDb indexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@addPeekWorkerTask(retries=1)
def compileDocumentChunk(payloadEncodedArgs: bytes) -> dict[str, str]:
    """Compile DocDb Index Task


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
                _compileDocumentChunk(conn, modelSetId, modelSetQueueItems)
            )

        queueTable = DocDbCompilerQueue.__table__

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


def _compileDocumentChunk(
    conn, modelSetId: int, queueItems: List[DocDbCompilerQueue]
) -> dict[str, str]:
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    compiledTable = DocDbEncodedChunk.__table__
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
        docDbIndexChunkEncodedPayload,
    ) in encKwPayloadByChunkKey.items():
        m = hashlib.sha256()
        m.update(docDbIndexChunkEncodedPayload)
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
                encodedData=docDbIndexChunkEncodedPayload,
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
            DocDbDocument, len(inserts)
        )
        for insert in inserts:
            insert["id"] = next(newIdGen)

    if inserts:
        conn.execute(compiledTable.insert(), inserts)

    logger.debug(
        "Compiled %s Documents, %s missing, in %s",
        len(inserts),
        len(chunkKeys) - len(inserts),
        (datetime.now(pytz.utc) - startTime),
    )

    total += len(inserts)

    logger.info(
        "Compiled and Committed %s EncodedDocumentChunks in %s",
        total,
        (datetime.now(pytz.utc) - startTime),
    )

    return lastUpdateByChunkKey


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = DocDbEncodedChunk.__table__

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
                DocDbDocument.chunkKey,
                DocDbDocument.key,
                DocDbDocument.documentJson,
            )
            .filter(DocDbDocument.chunkKey.in_(chunkKeys))
            .order_by(DocDbDocument.key)
            .yield_per(1000)
            .all()
        )

        # Create the ChunkKey -> {id -> packedJson, id -> packedJson, ....]
        packagedJsonByObjIdByChunkKey = defaultdict(dict)

        for item in indexQry:
            packagedJsonByObjIdByChunkKey[item.chunkKey][
                item.key
            ] = item.documentJson

        encPayloadByChunkKey = {}

        # Sort each bucket by the key
        for chunkKey, packedJsonByKey in packagedJsonByObjIdByChunkKey.items():
            tuples = json.dumps(packedJsonByKey, sort_keys=True)

            # Create the blob data for this index.
            # It will be docDbed by a binary sort
            encPayloadByChunkKey[chunkKey] = (
                Payload(tuples=tuples).toEncodedPayload().encode()
            )

        return encPayloadByChunkKey

    finally:
        session.close()

import logging
from datetime import datetime

import pytz
from sqlalchemy import delete
from sqlalchemy import distinct
from sqlalchemy import select


from peek_core_docdb._private.storage.DocDbCompilerQueue import (
    DocDbCompilerQueue,
)
from peek_core_docdb._private.storage.DocDbDocument import DocDbDocument
from peek_core_docdb._private.worker.tasks.ImportTask import _loadModelSets
from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_base.worker.task import addPeekWorkerTask


logger = logging.getLogger(__name__)


# We need to insert the into the following tables:


@addPeekWorkerTask()
def deleteDocumentsForImportGropHashTask(
    modelSetKey: str, importGroupHash: str
) -> None:
    startTime = datetime.now(pytz.utc)

    modelSetIdByKey = _loadModelSets()

    # Do the import
    try:
        modelSetId = modelSetIdByKey.get(modelSetKey)
        _deleteObjectsAndQueueChunkCompile(modelSetId, importGroupHash)

        logger.info(
            f"Deleted Documents for"
            f" modelSetKey={modelSetKey},"
            f" importGroupHash='{importGroupHash}',"
            f" in {datetime.now(pytz.utc) - startTime}"
        )

    except Exception as e:
        logger.debug("Retrying import docDb objects, %s", e)
        raise


def _deleteObjectsAndQueueChunkCompile(
    modelSetId: int, importGroupHash: str
) -> None:
    """Insert or Update Objects

    1) Get the chunks we need to recompile
    2) Delete the required objects
    3) Queue the chunks for recompile

    """

    documentTable = DocDbDocument.__table__
    queueTable = DocDbCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    engine = TaskDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:

        chunkKeyQuery = select(distinct(documentTable.c.chunkKey)).where(
            documentTable.c.importGroupHash == importGroupHash,
            documentTable.c.modelSetId == modelSetId,
        )

        chunkKeysToQueue = conn.execute(chunkKeyQuery).scalars().all()

        deleteStmt = delete(DocDbDocument).where(
            documentTable.c.importGroupHash == importGroupHash,
            documentTable.c.modelSetId == modelSetId,
        )

        result = conn.execute(deleteStmt)
        deletedDocCount = result.rowcount

        if chunkKeysToQueue:
            conn.execute(
                queueTable.insert(),
                [
                    dict(modelSetId=modelSetId, chunkKey=c)
                    for c in chunkKeysToQueue
                ],
            )

        if deletedDocCount or chunkKeysToQueue:
            transaction.commit()
        else:
            transaction.rollback()

        logger.debug(
            "Deleted %s, queued %s chunks in %s",
            deletedDocCount,
            len(chunkKeysToQueue),
            (datetime.now(pytz.utc) - startTime),
        )

    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()

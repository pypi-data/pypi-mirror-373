import logging

from twisted.internet.defer import inlineCallbacks

from peek_core_docdb._private.worker.tasks.ImportTask import (
    createOrUpdateDocuments,
)

from peek_core_docdb._private.worker.tasks.DeleteTask import (
    deleteDocumentsForImportGropHashTask,
)

logger = logging.getLogger(__name__)


class ImportController:
    def __init__(self):
        pass

    def shutdown(self):
        pass

    @inlineCallbacks
    def createOrUpdateDocuments(self, documentsEncodedPayload: bytes):
        yield createOrUpdateDocuments.delay(documentsEncodedPayload)

    @inlineCallbacks
    def deleteDocumentsForImportGropHash(
        self, modelSetKey: str, importGroupHash: str
    ):
        yield deleteDocumentsForImportGropHashTask.delay(
            modelSetKey, importGroupHash
        )

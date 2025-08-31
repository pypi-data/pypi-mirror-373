import logging

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_core_docdb._private.PluginNames import docDbFilt
from peek_core_docdb._private.server.client_handlers.ClientChunkLoadRpc import (
    ClientChunkLoadRpc,
)
from peek_core_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk
from peek_core_docdb._private.tuples.DocumentUpdateDateTuple import (
    DocumentUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientDocumentUpdateFromServerFilt = dict(key="clientDocumentUpdateFromServer")
clientDocumentUpdateFromServerFilt.update(docDbFilt)


class DocumentCacheController(ACICacheControllerABC):
    """Document Cache Controller

    The Document cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _ChunkedTuple = DocDbEncodedChunk
    _UpdateDateTupleABC = DocumentUpdateDateTuple
    _chunkLoadRpcMethod = ClientChunkLoadRpc.loadDocumentChunks
    _chunkIndexDeltaRpcMethod = ClientChunkLoadRpc.loadDocumentIndexDelta
    _updateFromLogicFilt = clientDocumentUpdateFromServerFilt
    _logger = logger

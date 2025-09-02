import logging
from typing import Optional

from vortex.Tuple import Tuple

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_core_docdb._private.tuples.DocumentUpdateDateTuple import (
    DocumentUpdateDateTuple,
)
from peek_plugin_base.PeekVortexUtil import peekServerName, peekBackendNames
from peek_core_docdb._private.PluginNames import docDbFilt
from peek_core_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class ClientChunkLoadRpc(ACIChunkLoadRpcABC):
    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadDocumentChunks.start(funcSelf=self)
        yield self.loadDocumentIndexDelta.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=docDbFilt,
        deferToThread=True,
    )
    def loadDocumentIndexDelta(self, indexEncodedPayload: bytes) -> bytes:
        return self.ckiChunkIndexDeltaBlocking(
            indexEncodedPayload, DocDbEncodedChunk, DocumentUpdateDateTuple
        )

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=docDbFilt,
        deferToThread=True,
    )
    def loadDocumentChunks(self, chunkKeys: list[str]) -> list[Tuple]:
        return self.ckiInitialLoadChunksPayloadBlocking(
            chunkKeys, DocDbEncodedChunk
        )

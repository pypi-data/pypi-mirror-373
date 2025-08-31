import logging
from typing import Union

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_docdb._private.client.controller.DocumentCacheController import (
    DocumentCacheController,
)

logger = logging.getLogger(__name__)


class ClientDocumentUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: DocumentCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        encodedPayload = self._cacheHandler.offlineUpdateDateTuplePayload()
        payloadEnvelope = PayloadEnvelope(filt, encodedPayload=encodedPayload)
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg

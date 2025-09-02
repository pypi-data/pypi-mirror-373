import logging
from typing import Union

from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import (
    ItemKeyIndexCacheController,
)

logger = logging.getLogger(__name__)


class ItemKeyIndexUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: ItemKeyIndexCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(
        self, filt: dict, tupleSelector: TupleSelector
    ) -> Union[Deferred, bytes]:
        encodedPayload = self._cacheHandler.offlineUpdateDateTuplePayload()
        payloadEnvelope = PayloadEnvelope(filt, encodedPayload=encodedPayload)
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg

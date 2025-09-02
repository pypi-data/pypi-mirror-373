import logging
from typing import Dict
from typing import List

from twisted.internet.defer import inlineCallbacks

from peek_abstract_chunked_index.private.client.handlers.ACICacheHandlerABC import (
    ACICacheHandlerABC,
)
from peek_abstract_chunked_index.private.tuples import ACIUpdateDateTupleABC
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import (
    SegmentCacheController,
)
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import (
    clientSegmentUpdateFromServerFilt,
)
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import (
    SegmentIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)

clientSegmentWatchUpdateFromDeviceFilt = {
    "key": "clientSegmentWatchUpdateFromDevice"
}
clientSegmentWatchUpdateFromDeviceFilt.update(graphDbFilt)


# ModelSet HANDLER
class SegmentCacheHandler(ACICacheHandlerABC):
    _UpdateDateTuple: ACIUpdateDateTupleABC = SegmentIndexUpdateDateTuple
    _updateFromDeviceFilt: Dict = clientSegmentWatchUpdateFromDeviceFilt
    _updateFromLogicFilt: Dict = clientSegmentUpdateFromServerFilt
    _logger: logging.Logger = logger

    @inlineCallbacks
    def notifyOfUpdate(self, chunkKeys: List[str]):
        assert isinstance(
            self._cacheController, SegmentCacheController
        ), "We expected SegmentCacheController"
        yield self._cacheController.notifyFastGraphDbModelChunkKeysUpdated(
            chunkKeys
        )
        yield ACICacheHandlerABC.notifyOfUpdate(self, chunkKeys)

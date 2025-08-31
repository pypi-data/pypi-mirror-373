import logging
from collections import defaultdict
from typing import Dict, List, Any

from peek_abstract_chunked_index.private.client.controller.ACICacheControllerABC import (
    ACICacheControllerABC,
)
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.SegmentIndexChunkLoadRpc import (
    SegmentIndexChunkLoadRpc,
)
from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import (
    GraphDbEncodedChunkTuple,
)
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import (
    SegmentIndexUpdateDateTuple,
)
from twisted.internet.defer import inlineCallbacks

logger = logging.getLogger(__name__)

clientSegmentUpdateFromServerFilt = dict(key="clientSegmentUpdateFromServer")
clientSegmentUpdateFromServerFilt.update(graphDbFilt)


class SegmentCacheController(ACICacheControllerABC):
    """Segment Cache Controller

    The Segment cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    _ChunkedTuple = GraphDbEncodedChunkTuple
    _UpdateDateTupleABC = SegmentIndexUpdateDateTuple
    _chunkLoadRpcMethod = SegmentIndexChunkLoadRpc.loadSegmentChunks
    _chunkIndexDeltaRpcMethod = SegmentIndexChunkLoadRpc.loadSegmentIndexDelta
    _updateFromLogicFilt = clientSegmentUpdateFromServerFilt
    _logger = logger

    def setFastGraphDb(self, fastGraphDb):
        self._fastGraphDb = fastGraphDb

    def shutdown(self):
        ACICacheControllerABC.shutdown(self)
        self._fastGraphDb = None

    @inlineCallbacks
    def notifyFastGraphDbModelChunkKeysUpdated(self, chunkKeys: List[Any]):
        chunkKeysUpdatedByModelSet: Dict[str, List[str]] = defaultdict(list)
        for chunkKey in chunkKeys:
            modelSetKey = chunkKey.split(".")[0]
            chunkKeysUpdatedByModelSet[modelSetKey].append(chunkKey)

        for modelSetKey, updatedChunkKeys in chunkKeysUpdatedByModelSet.items():
            fastGraphDbModel = self._fastGraphDb.graphForModelSet(modelSetKey)
            yield fastGraphDbModel.notifyOfUpdate(chunkKeys)

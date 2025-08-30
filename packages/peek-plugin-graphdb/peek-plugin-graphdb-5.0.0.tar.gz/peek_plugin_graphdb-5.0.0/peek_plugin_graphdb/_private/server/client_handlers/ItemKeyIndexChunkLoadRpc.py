import logging

from vortex.Tuple import Tuple
from vortex.rpc.RPC import vortexRPC

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import (
    ACIChunkLoadRpcABC,
)
from peek_plugin_base.PeekVortexUtil import peekBackendNames
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import (
    ItemKeyIndexEncodedChunk,
)
from peek_plugin_graphdb._private.tuples.ItemKeyIndexUpdateDateTuple import (
    ItemKeyIndexUpdateDateTuple,
)

logger = logging.getLogger(__name__)


class ItemKeyIndexChunkLoadRpc(ACIChunkLoadRpcABC):
    def makeHandlers(self):
        """Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadItemKeyIndexChunks.start(funcSelf=self)
        yield self.loadItemKeyIndexDelta.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=graphDbFilt,
        deferToThread=True,
    )
    def loadItemKeyIndexDelta(self, indexEncodedPayload: bytes) -> bytes:
        return self.ckiChunkIndexDeltaBlocking(
            indexEncodedPayload,
            ItemKeyIndexEncodedChunk,
            ItemKeyIndexUpdateDateTuple,
        )

    # -------------
    @vortexRPC(
        peekServerName,
        acceptOnlyFromVortex=peekBackendNames,
        timeoutSeconds=120,
        additionalFilt=graphDbFilt,
        deferToThread=True,
    )
    def loadItemKeyIndexChunks(self, chunkKeys: list[str]) -> list[Tuple]:
        return self.ckiInitialLoadChunksPayloadBlocking(
            chunkKeys, ItemKeyIndexEncodedChunk
        )

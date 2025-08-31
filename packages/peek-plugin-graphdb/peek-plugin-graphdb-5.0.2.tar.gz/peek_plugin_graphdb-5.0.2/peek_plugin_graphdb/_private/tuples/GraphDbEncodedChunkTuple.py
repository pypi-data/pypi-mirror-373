import logging

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)

logger = logging.getLogger(__name__)


@addTupleType
class GraphDbEncodedChunkTuple(Tuple, ACIEncodedChunkTupleABC):
    __tupleType__ = graphDbTuplePrefix + "GraphDbEncodedChunkTuple"

    modelSetKey: str = TupleField()

    chunkKey: str = TupleField()
    encodedData: bytes = TupleField()
    encodedHash: str = TupleField()
    lastUpdate: str = TupleField()

    @property
    def ckiChunkKey(self):
        return self.chunkKey

    @property
    def ckiEncodedData(self):
        return self.encodedData

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedData)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

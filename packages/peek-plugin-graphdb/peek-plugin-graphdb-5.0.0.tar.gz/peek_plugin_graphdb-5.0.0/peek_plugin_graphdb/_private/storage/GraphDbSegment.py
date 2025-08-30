from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet


@addTupleType
class GraphDbSegment(DeclarativeBase, Tuple):
    __tupleType__ = graphDbTuplePrefix + "GraphDbSegmentTable"
    __tablename__ = "GraphDbSegment"

    #:  The unique ID of this segment (database generated)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    #:  The model set for this segment
    modelSetId = Column(
        Integer,
        ForeignKey("GraphDbModelSet.id", ondelete="CASCADE"),
        nullable=False,
    )
    modelSet = relationship(GraphDbModelSet)

    importGroupHash = Column(String, nullable=False)

    #:  The unique key of this segment
    key = Column(String, nullable=False)

    #:  The chunk that this segment fits into
    chunkKey = Column(String, nullable=False)

    #:  The segment data
    segmentJson = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_Segment_key", modelSetId, key, unique=True),
        Index("idx_Segment_gridKey", chunkKey, unique=False),
        Index("idx_Segment_importGroupHash", importGroupHash, unique=False),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

from sqlalchemy import Boolean
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
from peek_plugin_graphdb._private.storage.GraphDbTraceConfigRule import (
    GraphDbTraceConfigRule,
)
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import (
    GraphDbTraceConfigTuple,
)


@addTupleType
class GraphDbTraceConfig(DeclarativeBase, Tuple):
    __tupleType__ = graphDbTuplePrefix + "GraphDbTraceConfigTable"
    __tablename__ = "GraphDbTraceConfig"

    #:  The unique ID of this segment (database generated)
    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this segment
    modelSetId = Column(
        Integer,
        ForeignKey("GraphDbModelSet.id", ondelete="CASCADE"),
        nullable=False,
    )
    modelSet = relationship(GraphDbModelSet)

    #:  The unique key of this segment
    key = Column(String, nullable=False)

    #:  The unique name of this segment
    name = Column(String, nullable=False)

    #:  The title to describe this segment
    title = Column(String, nullable=False)

    #:  The comment for this config
    comment = Column(String)

    #:  Is this trace config enabled
    isEnabled = Column(Boolean, nullable=False, server_default="true")

    #: The relationship for the rules
    rules = relationship(
        "GraphDbTraceConfigRule", lazy="joined", overlaps="traceConfig"
    )

    __table_args__ = (
        Index("idx_TraceConfig_key", modelSetId, key, unique=True),
        Index("idx_TraceConfig_name", modelSetId, name, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def fromTuple(
        self, tupleIn: GraphDbTraceConfigTuple, modelSetId: int
    ) -> "GraphDbTraceConfig":
        self.modelSetId = modelSetId
        self.key = tupleIn.key
        self.name = tupleIn.name
        self.title = tupleIn.title
        self.comment = tupleIn.comment
        self.isEnabled = tupleIn.isEnabled

        self.rules = [
            GraphDbTraceConfigRule().fromTuple(rule, self.id)
            for rule in tupleIn.rules
        ]

        return self

    def toTuple(self) -> GraphDbTraceConfigTuple:
        traceTuple = GraphDbTraceConfigTuple(
            modelSetKey=self.modelSet.key,
            key=self.key,
            name=self.name,
            title=self.title,
            comment=self.comment,
            isEnabled=self.isEnabled,
        )

        traceTuple.rules = [rule.toTuple() for rule in self.rules]

        return traceTuple

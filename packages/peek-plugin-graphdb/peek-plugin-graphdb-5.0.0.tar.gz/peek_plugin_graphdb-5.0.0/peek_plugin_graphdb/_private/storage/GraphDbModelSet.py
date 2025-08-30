from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbModelSetTuple import GraphDbModelSetTuple
from .DeclarativeBase import DeclarativeBase


@addTupleType
class GraphDbModelSet(DeclarativeBase, Tuple):
    __tablename__ = "GraphDbModelSet"
    __tupleType__ = graphDbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    comment = Column(String)
    propsJson = Column(String)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def toTuple(self) -> GraphDbModelSetTuple:
        return GraphDbModelSetTuple(
            id=self.id,
            key=self.key,
            name=self.name,
            comment=self.comment,
            propsJson=self.propsJson,
        )


def getOrCreateGraphDbModelSet(session, modelSetName: str) -> GraphDbModelSet:
    qry = session.query(GraphDbModelSet).filter(
        GraphDbModelSet.name == modelSetName
    )
    if not qry.count():
        session.add(GraphDbModelSet(name=modelSetName))
        session.commit()

    return qry.one()

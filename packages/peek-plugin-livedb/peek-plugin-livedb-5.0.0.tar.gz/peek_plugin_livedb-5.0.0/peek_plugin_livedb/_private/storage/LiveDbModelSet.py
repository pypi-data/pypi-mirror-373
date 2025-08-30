from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix
from .DeclarativeBase import DeclarativeBase


@addTupleType
class LiveDbModelSet(DeclarativeBase, Tuple):
    __tablename__ = "LiveDbModelSet"
    __tupleType__ = livedbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    comment = Column(String)

    propsJson = Column(String)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)


def getOrCreateLiveDbModelSet(session, modelSetKey: str) -> LiveDbModelSet:
    qry = session.query(LiveDbModelSet).filter(
        LiveDbModelSet.key == modelSetKey
    )
    if not qry.count():
        session.add(LiveDbModelSet(key=modelSetKey, name=modelSetKey))
        session.commit()

    return qry.one()

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from .DeclarativeBase import DeclarativeBase


@addTupleType
class EventDBModelSetTable(DeclarativeBase, Tuple):
    __tablename__ = "EventDBModelSet"
    __tupleType__ = eventdbTuplePrefix + "EventDBModelSetTable"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    comment = Column(String)

    propsJson = Column(String)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)


def getOrCreateEventDBModelSet(
    session, modelSetKey: str
) -> EventDBModelSetTable:
    qry = session.query(EventDBModelSetTable).filter(
        EventDBModelSetTable.key == modelSetKey
    )
    if not qry.count():
        session.add(EventDBModelSetTable(key=modelSetKey, name=modelSetKey))
        session.commit()

    return qry.one()

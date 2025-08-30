from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from .DeclarativeBase import DeclarativeBase
from .EventDBPropertyTable import EventDBPropertyTable
from ...tuples.EventDBPropertyValueTuple import EventDBPropertyValueTuple


@addTupleType
class EventDBPropertyValueTable(DeclarativeBase, Tuple):
    __tablename__ = "EventDBPropertyValue"
    __tupleType__ = eventdbTuplePrefix + "EventDBPropertyValueTable"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    color = Column(String)
    comment = Column(String)

    propertyId = Column(
        Integer,
        ForeignKey("EventDBProperty.id", ondelete="CASCADE"),
        nullable=False,
    )
    property = relationship(EventDBPropertyTable, backref="values")

    __table_args__ = (
        Index("idx_EventDBPropVal_name", propertyId, name, unique=True),
        Index("idx_EventDBPropVal_value", propertyId, value, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def toTuple(self) -> EventDBPropertyValueTuple:
        return EventDBPropertyValueTuple(
            name=self.name,
            value=self.value,
            color=self.color,
            comment=self.comment,
        )

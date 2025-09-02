from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_plugin_eventdb._private.PluginNames import eventdbTuplePrefix
from .DeclarativeBase import DeclarativeBase
from .EventDBModelSetTable import EventDBModelSetTable
from ...tuples.EventDBPropertyTuple import EventDBPropertyTuple


@addTupleType
class EventDBPropertyTable(DeclarativeBase, Tuple):
    __tablename__ = "EventDBProperty"
    __tupleType__ = eventdbTuplePrefix + "EventDBPropertyTable"

    SHOW_FILTER_AS_FREE_TEXT = 1
    SHOW_FILTER_SELECT_MANY = 2
    SHOW_FILTER_SELECT_ONE = 3

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(
        Integer,
        ForeignKey("EventDBModelSet.id", ondelete="CASCADE"),
        nullable=False,
    )
    modelSet = relationship(EventDBModelSetTable)

    key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    comment = Column(String)

    useForFilter = Column(Boolean)
    useForDisplay = Column(Boolean)
    useForPopup = Column(Boolean)
    showFilterAs = Column(Integer)

    displayByDefaultOnSummaryView = Column(Boolean)
    displayByDefaultOnDetailView = Column(Boolean)

    valuesFromAdminUi = TupleField()

    __table_args__ = (
        Index("idx_EventDBProp_name", modelSetId, key, unique=True),
        Index("idx_EventDBProp_value", modelSetId, name, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

    def toTuple(self) -> EventDBPropertyTuple:
        return EventDBPropertyTuple(
            modelSetKey=self.modelSet.key,
            key=self.key,
            name=self.name,
            order=self.order,
            comment=self.comment,
            useForFilter=self.useForFilter,
            useForDisplay=self.useForDisplay,
            useForPopup=self.useForPopup,
            displayByDefaultOnSummaryView=self.displayByDefaultOnSummaryView,
            displayByDefaultOnDetailView=self.displayByDefaultOnDetailView,
            showFilterAs=self.showFilterAs,
            values=[v.toTuple() for v in self.values],
        )

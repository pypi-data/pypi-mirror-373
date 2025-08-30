from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.DeclarativeBase import DeclarativeBase


@addTupleType
class SearchPropertyTuple(DeclarativeBase, Tuple):
    __tupleType__ = searchTuplePrefix + "SearchPropertyTuple"
    __tablename__ = "SearchProperty"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    order = Column(Integer, nullable=False, server_default="0")

    showOnResult = Column(Boolean, nullable=False, server_default="1")
    showInHeader = Column(Boolean, nullable=False, server_default="0")

    __table_args__ = (
        Index("idx_SearchProp_name", name, unique=True),
        Index("idx_SearchProp_title", title, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

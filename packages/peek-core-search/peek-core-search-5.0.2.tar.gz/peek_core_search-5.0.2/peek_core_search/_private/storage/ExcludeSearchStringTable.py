from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.DeclarativeBase import DeclarativeBase


@addTupleType
class ExcludeSearchStringTable(DeclarativeBase, Tuple):
    __tupleType__ = searchTuplePrefix + "ExcludeSearchStringTable"
    __tablename__ = "ExcludeSearchString"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String, nullable=False)
    partial = Column(Boolean, nullable=True)
    full = Column(Boolean, nullable=True)
    comment = Column(String, nullable=True)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

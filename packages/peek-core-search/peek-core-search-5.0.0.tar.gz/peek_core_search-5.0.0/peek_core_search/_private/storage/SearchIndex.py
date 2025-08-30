import logging

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_search._private.PluginNames import searchTuplePrefix
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class SearchIndex(DeclarativeBase, Tuple):
    __tablename__ = "SearchIndex"
    __tupleType__ = searchTuplePrefix + "SearchIndexTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    chunkKey = Column(String, nullable=False)
    keyword = Column(String, nullable=False)
    propertyName = Column(String, nullable=False)

    #:  The object that this routs is for
    objectId = Column(
        BigInteger,
        ForeignKey("SearchObject.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "idx_SearchIndex_quick_query",
            chunkKey,
            keyword,
            propertyName,
            objectId,
            unique=True,
        ),
        Index("idx_SearchIndex_objectId", objectId),  # For foreign key
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

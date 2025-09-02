import logging

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Integer
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
class SearchObject(DeclarativeBase, Tuple):
    __tablename__ = "SearchObject"
    __tupleType__ = searchTuplePrefix + "SearchObjectTable"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    #:  The object that this routs is for
    objectTypeId = Column(
        Integer,
        ForeignKey("SearchObjectType.id", ondelete="CASCADE"),
        nullable=False,
    )

    key = Column(String, nullable=False)

    chunkKey = Column(String, nullable=False)

    fullKwPropertiesJson = Column(String, nullable=True)

    partialKwPropertiesJson = Column(String, nullable=True)

    packedJson = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_SearchObject_objectTypeId", objectTypeId),
        Index("idx_SearchObject_key", key, unique=True),
        Index("idx_SearchObject_chunkKey", chunkKey),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

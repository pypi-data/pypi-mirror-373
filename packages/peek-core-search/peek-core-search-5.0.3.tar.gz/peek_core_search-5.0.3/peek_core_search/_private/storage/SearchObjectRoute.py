import logging

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
class SearchObjectRoute(DeclarativeBase, Tuple):
    """Search Object Route

    This is like the "Open with"

    """

    __tablename__ = "SearchObjectRoute"
    __tupleType__ = searchTuplePrefix + "SearchObjectRouteTable"

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The object that this routs is for
    objectId = Column(
        Integer,
        ForeignKey("SearchObject.id", ondelete="CASCADE"),
        nullable=False,
    )

    importGroupHash = Column(String, nullable=False)
    routeTitle = Column(String, nullable=False)
    routePath = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ObjectRoute_objectId", objectId),  # For foreign key
        Index(
            "idx_ObjectRoute_routeTitle_importGroupHash",
            importGroupHash,
            unique=False,
        ),
        Index(
            "idx_ObjectRoute_routeTitle_objectId",
            routeTitle,
            objectId,
            unique=True,
        ),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

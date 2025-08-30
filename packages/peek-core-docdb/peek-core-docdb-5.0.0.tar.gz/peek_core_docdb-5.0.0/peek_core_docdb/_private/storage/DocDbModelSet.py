from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_docdb._private.PluginNames import docDbTuplePrefix
from .DeclarativeBase import DeclarativeBase


@addTupleType
class DocDbModelSet(DeclarativeBase, Tuple):
    __tablename__ = "DocDbModelSet"
    __tupleType__ = docDbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    comment = Column(String)
    propsJson = Column(String)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

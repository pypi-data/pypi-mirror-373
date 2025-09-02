from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_core_docdb._private.PluginNames import docDbTuplePrefix
from peek_core_docdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_docdb._private.storage.DocDbModelSet import DocDbModelSet


@addTupleType
class DocDbDocumentTypeTuple(DeclarativeBase, Tuple):
    __tupleType__ = docDbTuplePrefix + "DocDbDocumentTypeTuple"
    __tablename__ = "DocDbDocumentType"

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this document
    modelSetId = Column(
        Integer,
        ForeignKey("DocDbModelSet.id", ondelete="CASCADE"),
        nullable=False,
    )
    modelSet = relationship(DocDbModelSet)

    name = Column(String, nullable=False)
    title = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_DocType_model_name", modelSetId, name, unique=True),
        Index("idx_DocType_model_title", modelSetId, title, unique=True),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

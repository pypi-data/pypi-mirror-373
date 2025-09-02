from sqlalchemy import BigInteger
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
from peek_core_docdb._private.storage.DocDbDocumentTypeTuple import (
    DocDbDocumentTypeTuple,
)
from peek_core_docdb._private.storage.DocDbModelSet import DocDbModelSet


@addTupleType
class DocDbDocument(DeclarativeBase, Tuple):
    __tupleType__ = docDbTuplePrefix + "DocDbDocumentTable"
    __tablename__ = "DocDbDocument"

    #:  The unique ID of this document (database generated)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    #:  The model set for this document
    modelSetId = Column(
        Integer,
        ForeignKey("DocDbModelSet.id", ondelete="CASCADE"),
        nullable=False,
    )
    modelSet = relationship(DocDbModelSet)

    #:  The model set for this document
    documentTypeId = Column(
        Integer,
        ForeignKey("DocDbDocumentType.id", ondelete="CASCADE"),
        nullable=False,
    )
    documentType = relationship(DocDbDocumentTypeTuple)

    importGroupHash = Column(String, nullable=False)

    #:  The unique key of this document
    key = Column(String, nullable=False)

    #:  The chunk that this document fits into
    chunkKey = Column(String, nullable=False)

    #:  The document data
    documentJson = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_Document_key", modelSetId, key, unique=True),
        Index("idx_Document_documentType", documentTypeId, unique=False),
        Index("idx_Document_gridKey", chunkKey, unique=False),
        Index("idx_Document_importGroupHash", importGroupHash, unique=False),
    )

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_docdb_generic_menu._private.PluginNames import (
    docDbGenericMenuTuplePrefix,
)
from peek_plugin_docdb_generic_menu._private.storage.DeclarativeBase import (
    DeclarativeBase,
)


@addTupleType
class DocDbGenericMenuTuple(DeclarativeBase, Tuple):
    __tupleType__ = docDbGenericMenuTuplePrefix + "DocDbGenericMenuTuple"
    __tablename__ = "Menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    modelSetKey = Column(String)
    coordSetKey = Column(String)
    faIcon = Column(String)
    title = Column(String)
    tooltip = Column(String)
    url = Column(String, nullable=False)
    showCondition = Column(String, nullable=True)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

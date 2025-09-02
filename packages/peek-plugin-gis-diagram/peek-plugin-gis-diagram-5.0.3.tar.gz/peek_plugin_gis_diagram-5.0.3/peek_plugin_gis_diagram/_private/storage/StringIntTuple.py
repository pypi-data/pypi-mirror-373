from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import orm
from vortex.Tuple import Tuple
from vortex.Tuple import addTupleType

from peek_plugin_gis_diagram._private.PluginNames import gisDiagramTuplePrefix
from peek_plugin_gis_diagram._private.storage.DeclarativeBase import (
    DeclarativeBase,
)


@addTupleType
class StringIntTuple(DeclarativeBase, Tuple):
    __tupleType__ = gisDiagramTuplePrefix + "StringIntTuple"
    __tablename__ = "StringIntTuple"

    id = Column(Integer, primary_key=True, autoincrement=True)
    string1 = Column(String(50))
    int1 = Column(Integer)

    @orm.reconstructor
    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)

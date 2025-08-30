from typing import Any

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class SimpleSubprocTaskConstructorTuple(Tuple):
    __tablename__ = "SimpleSubprocTaskConstructorTuple"
    __tupleType__ = "peek_plugin_base." + __tablename__

    # Call arguments
    kwargs: dict[str, Any] = TupleField()

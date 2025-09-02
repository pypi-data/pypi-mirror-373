from typing import Any

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class SimpleSubprocTaskCallTuple(Tuple):
    __tablename__ = "SimpleSubprocTaskCallTuple"
    __tupleType__ = "peek_plugin_base." + __tablename__

    # Subprocess fields
    commandUuid: str = TupleField()

    # Call arguments
    kwargs: dict[str, Any] = TupleField()

from typing import Any
from typing import Optional

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class SimpleSubprocTaskResultTuple(Tuple):
    __tablename__ = "SimpleSubprocTaskResultTuple"
    __tupleType__ = "peek_plugin_base." + __tablename__

    # Subprocess fields
    commandUuid: str = TupleField()
    exceptionStr: Optional[str] = TupleField()

    # Result values
    result: Any = TupleField()

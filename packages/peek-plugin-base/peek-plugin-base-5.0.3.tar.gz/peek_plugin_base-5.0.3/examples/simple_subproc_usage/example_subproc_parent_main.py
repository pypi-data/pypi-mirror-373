import os
import sys
import uuid

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks

from examples.simple_subproc_usage import example_subproc_child_main
from peek_plugin_base.simple_subproc.simple_subproc_parent_protocol import (
    SimpleSubprocParentProtocol,
)
from peek_plugin_base.simple_subproc.simple_subproc_task_call_tuple import (
    SimpleSubprocTaskCallTuple,
)
from peek_plugin_base.simple_subproc.simple_subproc_task_constructor_tuple import (
    SimpleSubprocTaskConstructorTuple,
)


class ExampleSubprocParentMain:
    def __init__(self, constructorArg1: str, constructorArg2: bool):
        self._processProtocol = SimpleSubprocParentProtocol(
            SimpleSubprocTaskConstructorTuple(
                kwargs=dict(
                    constructorArg1=constructorArg1,
                    constructorArg2=constructorArg2,
                )
            )
        )

        self._processTransport = reactor.spawnProcess(
            self._processProtocol,
            sys.executable,
            args=[sys.executable, example_subproc_child_main.__file__],
            env={
                "HOME": os.environ["HOME"],
                "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", ""),
                "DYLD_LIBRARY_PATH": os.environ.get("DYLD_LIBRARY_PATH", ""),
                "ORACLE_HOME": os.environ["ORACLE_HOME"],
            },
            path=os.path.dirname(example_subproc_child_main.__file__),
        )

    @inlineCallbacks
    def apply_async(self, runArg1: str, runArg2: bool) -> Deferred:
        importCommandTuple = SimpleSubprocTaskCallTuple(
            commandUuid=str(uuid.uuid4()),
            kwargs=dict(runArg1=runArg1, runArg2=runArg2),
        )

        # noinspection PyTypeChecker
        strResult, boolResult = yield self._processProtocol.queueCommand(
            importCommandTuple
        )

        return strResult, boolResult

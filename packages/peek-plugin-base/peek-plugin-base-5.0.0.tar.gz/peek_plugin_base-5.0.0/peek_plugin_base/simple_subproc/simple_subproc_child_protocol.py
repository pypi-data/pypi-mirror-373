import json
import logging
import sys
from base64 import b64decode
from base64 import b64encode

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import connectionDone
from twisted.python import failure

from peek_plugin_base.simple_subproc.simple_subproc_task_call_tuple import (
    SimpleSubprocTaskCallTuple,
)
from peek_plugin_base.simple_subproc.simple_subproc_task_constructor_tuple import (
    SimpleSubprocTaskConstructorTuple,
)
from peek_plugin_base.simple_subproc.simple_subproc_task_result_tuple import (
    SimpleSubprocTaskResultTuple,
)


logger = logging.getLogger("simple_subproc_child_protocol")


class SimpleSubprocChildProtocol(protocol.Protocol):
    def __init__(self, TaskClass):
        self._data = b""
        self._delegate = None
        self._Delegate = TaskClass

        logging.basicConfig(
            level=logging.DEBUG,
            stream=sys.stderr,
            format="%(levelname)s:%(message)s",
        )

    @inlineCallbacks
    def dataReceived(self, data: bytes):
        self._data += data

        while b"." in self._data:
            message, self._data = self._data.split(b".", 1)
            if not message:
                continue

            if not self._delegate:
                logger.debug("Received constructor data")
                self._constructClass(message)
                continue

            yield self._runTask(message)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        logger.debug("STDIN closed, we'll stop the reactor in 5 seconds")
        reactor.callLater(5, reactor.stop)

    def _constructClass(self, message: bytes):
        constructorTuple = SimpleSubprocTaskConstructorTuple().fromJsonDict(
            json.loads(b64decode(message))
        )
        self._delegate = self._Delegate(**constructorTuple.kwargs)

    @inlineCallbacks
    def _runTask(self, message: bytes):
        # logging.info("Received load data")
        importCommandTuple = SimpleSubprocTaskCallTuple().fromJsonDict(
            json.loads(b64decode(message))
        )
        try:
            result = yield self._delegate.run(**importCommandTuple.kwargs)

            resultTuple = SimpleSubprocTaskResultTuple(
                commandUuid=importCommandTuple.commandUuid, result=result
            )

        except Exception as e:
            logger.exception(str(e))
            resultTuple = SimpleSubprocTaskResultTuple(
                commandUuid=importCommandTuple.commandUuid, exceptionStr=str(e)
            )

        response = b64encode(json.dumps(resultTuple.toJsonDict()).encode())

        self.transport.write(response)
        self.transport.write(b".")

import json
import logging
from base64 import b64decode
from base64 import b64encode

from twisted.internet import protocol
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from .simple_subproc_task_call_tuple import SimpleSubprocTaskCallTuple
from .simple_subproc_task_constructor_tuple import (
    SimpleSubprocTaskConstructorTuple,
)
from .simple_subproc_task_result_tuple import SimpleSubprocTaskResultTuple

logger = logging.getLogger("simple_subproc_parent_protocol")


class SimpleSubprocParentProtocol(protocol.ProcessProtocol):
    def __init__(self, constructorTuple: SimpleSubprocTaskConstructorTuple):
        self._constructorTuple = constructorTuple
        self._data = b""
        self._logData = b""
        self._deferredByUuid = {}
        self._lastLoggerMethod = logger.error

    def connectionMade(self):
        self.transport.write(
            b64encode(json.dumps(self._constructorTuple.toJsonDict()).encode())
        )
        self.transport.write(b".")

    def errReceived(self, data: bytes):
        self._logData += data

        while b"\n" in self._logData:
            message, self._logData = self._logData.split(b"\n", 1)
            if not message:
                continue

            message = message.decode()

            # Filter out cryptography deprecation warnings
            if self._shouldFilterMessage(message):
                continue

            # Because some log lines have \n in them, we need to remember
            # the last log level
            if ":" in message:
                severity, logMsg = message.split(":", 1)
                if severity == "DEBUG":
                    self._lastLoggerMethod = logger.debug
                    message = logMsg
                elif severity == "INFO":
                    self._lastLoggerMethod = logger.info
                    message = logMsg
                elif severity == "WARNING":
                    self._lastLoggerMethod = logger.warning
                    message = logMsg
                elif severity == "ERROR":
                    self._lastLoggerMethod = logger.error
                    message = logMsg

            self._lastLoggerMethod(message)

    @inlineCallbacks
    def outReceived(self, data):
        self._data += data

        while b"." in self._data:
            message, self._data = self._data.split(b".", 1)
            if not message:
                continue

            resultTuple = yield self._decodeResult(message)

            d = self._deferredByUuid.pop(resultTuple.commandUuid)
            if resultTuple.exceptionStr:
                d.errback(Exception(resultTuple.exceptionStr))
            else:
                d.callback(resultTuple.result)

    @inlineCallbacks
    def queueCommand(self, command: SimpleSubprocTaskCallTuple) -> Deferred:
        d = Deferred()
        self._deferredByUuid[command.commandUuid] = d

        commandMessage = yield self._encodeCall(command)
        self.transport.write(commandMessage)
        self.transport.write(b".")
        return (yield d)

    @deferToThreadWrapWithLogger(logger)
    def _encodeCall(self, command):
        return b64encode(json.dumps(command.toJsonDict()).encode())

    def _shouldFilterMessage(self, message: str) -> bool:
        """Filter out known cryptography deprecation warnings"""
        filterPatterns = [
            "CryptographyDeprecationWarning: Blowfish",
            "CryptographyDeprecationWarning: CAST5",
            "blowfish-cbc",
            "cast128-cbc",
            "blowfish-ctr",
            "cast128-ctr",
            "twisted/conch/ssh/transport.py",
        ]
        return any(pattern in message for pattern in filterPatterns)

    @deferToThreadWrapWithLogger(logger)
    def _decodeResult(self, message):
        return SimpleSubprocTaskResultTuple().fromJsonDict(
            json.loads(b64decode(message))
        )

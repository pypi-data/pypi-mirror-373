import logging
import sys

from twisted.internet import reactor
from twisted.internet._posixstdio import StandardIO

from peek_plugin_base.simple_subproc.simple_subproc_child_protocol import (
    SimpleSubprocChildProtocol,
)

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)


class ExampleSubprocClass:
    def __init__(self, constructorArg1: str, constructorArg2: bool):
        self._constructorArg1 = constructorArg1
        self._constructorArg2 = constructorArg2

    def run(self, runArg1: str, runArg2: bool):
        return (
            f"{runArg1} + {self._constructorArg1}",
            self._constructorArg1 and runArg2,
        )

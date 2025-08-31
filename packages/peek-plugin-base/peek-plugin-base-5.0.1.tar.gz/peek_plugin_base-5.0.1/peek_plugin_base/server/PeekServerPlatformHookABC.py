from abc import abstractmethod
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union

from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import (
    PeekPlatformFileStorageHookABC,
)
from peek_plugin_base.server.PeekPlatformAdminHttpHookABC import (
    PeekPlatformAdminHttpHookABC,
)
from peek_plugin_base.server.PeekPlatformServerHttpHookABC import (
    PeekPlatformServerHttpHookABC,
)


class PeekServerPlatformHookABC(
    PeekPlatformCommonHookABC,
    PeekPlatformAdminHttpHookABC,
    PeekPlatformServerHttpHookABC,
    PeekPlatformFileStorageHookABC,
):
    @property
    @abstractmethod
    def dbConnectString(self) -> str:
        """DB Connect String

        :return: The SQLAlchemy database engine connection string/url.

        """

    @property
    @abstractmethod
    def dbEngineArgs(self) -> Optional[Dict[str, Union[str, int]]]:
        """DB Engine Args

        :return: The SQLAlchemy database engine arguments.

        """

    @property
    @abstractmethod
    def metricsWriteDirectory(self) -> Path:
        """Metrics Write Directory

        This method returns a Path object providing access to the managed
        file storage location where the plugin should periodically write
        its state.

        See https://docs.python.org/3/library/pathlib.html#basic-use

        :returns: The plugins managed metrics write Path object.
        """

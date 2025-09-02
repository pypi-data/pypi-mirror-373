from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import (
    PeekPlatformFileStorageHookABC,
)
from peek_plugin_base.PeekPlatformServerInfoHookABC import (
    PeekPlatformServerInfoHookABC,
)


class PeekWorkerPlatformHookABC(
    PeekPlatformCommonHookABC,
    PeekPlatformFileStorageHookABC,
    PeekPlatformServerInfoHookABC,
):
    pass

from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import (
    PeekPlatformFileStorageHookABC,
)
from peek_plugin_base.PeekPlatformServerInfoHookABC import (
    PeekPlatformServerInfoHookABC,
)
from peek_plugin_base.agent.PeekPlatformAgentHttpHookABC import (
    PeekPlatformAgentHttpHookABC,
)


class PeekAgentPlatformHookABC(
    PeekPlatformCommonHookABC,
    PeekPlatformServerInfoHookABC,
    PeekPlatformAgentHttpHookABC,
    PeekPlatformFileStorageHookABC,
):
    pass

from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.worker.peek_worker_platform_hook_abc import (
    PeekWorkerPlatformHookABC,
)


class PluginWorkerEntryHookABC(PluginCommonEntryHookABC):
    def __init__(
        self,
        pluginName: str,
        pluginRootDir: str,
        platform: PeekWorkerPlatformHookABC,
    ):
        PluginCommonEntryHookABC.__init__(
            self, pluginName=pluginName, pluginRootDir=pluginRootDir
        )
        self._platform = platform

    @property
    def platform(self) -> PeekWorkerPlatformHookABC:
        return self._platform

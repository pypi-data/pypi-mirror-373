import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from jsoncfg.value_mappers import require_string

from txhttputil.downloader.HttpResourceProxy import HttpResourceProxy

from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC

from peek_plugin_base.client.PeekClientPlatformHookABC import (
    PeekClientPlatformHookABC,
)

logger = logging.getLogger(__name__)


class PluginClientEntryHookABC(PluginCommonEntryHookABC):
    def __init__(
        self,
        pluginName: str,
        pluginRootDir: str,
        platform: PeekClientPlatformHookABC,
    ):
        PluginCommonEntryHookABC.__init__(
            self, pluginName=pluginName, pluginRootDir=pluginRootDir
        )
        self._platform = platform

    @property
    def platform(self) -> PeekClientPlatformHookABC:
        return self._platform

    @property
    def publishedClientApi(self) -> Optional[object]:
        return None

    @property
    def angularMainModule(self) -> str:
        """Angular Main Module

        :return: The name of the main module that the Angular2 router will lazy load.
        """
        return self._angularMainModule

    @property
    def angularFrontendAppDir(self) -> str:
        """Angular Frontend Dir

        This directory will be linked into the angular app when it is compiled.

        :return: The absolute path of the Angular2 app directory.
        """
        relDir = self._packageCfg.config.plugin.title(require_string)
        dir = os.path.join(self._pluginRoot, relDir)
        if not os.path.isdir(dir):
            raise NotADirectoryError(dir)
        return dir

    # TODO: Remove this, Plugins should access platform config via self.platform
    @property
    def platformConfig(self):
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config

    # TODO, Remove this
    def copyFolder(self, srcDir: Path, dstDir: Path):
        shutil.copytree(srcDir, dstDir, dirs_exist_ok=True)

    # TODO, Move this to PeekClientPlatformHookABC
    def createProxy(self) -> HttpResourceProxy:
        return HttpResourceProxy(
            self.platform.peekServerHost,
            self.platform.peekServerHttpPort,
            useSsl=self.platform.peekServerSSL,
            sslEnableMutualTLS=self.platform.peekServerSSLEnableMutualTLS,
            sslClientCertificateBundleFilePath=self.platform.peekServerSSLClientBundleFilePath,
            sslMutualTLSCertificateAuthorityBundleFilePath=self.platform.peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath,
            sslMutualTLSTrustedPeerCertificateBundleFilePath=self.platform.peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath,
        )

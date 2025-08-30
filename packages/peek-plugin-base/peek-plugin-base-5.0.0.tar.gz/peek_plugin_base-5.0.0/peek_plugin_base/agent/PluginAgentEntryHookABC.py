from typing import Optional

from txhttputil.downloader.HttpResourceProxy import HttpResourceProxy

from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.agent.PeekAgentPlatformHookABC import (
    PeekAgentPlatformHookABC,
)


class PluginAgentEntryHookABC(PluginCommonEntryHookABC):
    def __init__(
        self,
        pluginName: str,
        pluginRootDir: str,
        platform: PeekAgentPlatformHookABC,
    ):
        PluginCommonEntryHookABC.__init__(
            self, pluginName=pluginName, pluginRootDir=pluginRootDir
        )
        self._platform = platform

    @property
    def platform(self) -> PeekAgentPlatformHookABC:
        return self._platform

    @property
    def publishedAgentApi(self) -> Optional[object]:
        return None

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

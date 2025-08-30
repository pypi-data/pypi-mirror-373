from pathlib import Path
from typing import Optional

from peek_platform import PeekPlatformConfig
from peek_plugin_base.agent.PeekAgentPlatformHookABC import (
    PeekAgentPlatformHookABC,
)


class PeekAgentPlatformHook(PeekAgentPlatformHookABC):

    def __init__(self, pluginName: str) -> None:
        PeekAgentPlatformHookABC.__init__(self)
        self._pluginName = pluginName

    @property
    def fileStorageDirectory(self) -> Path:
        from peek_platform import PeekPlatformConfig

        return Path(PeekPlatformConfig.config.pluginDataPath(self._pluginName))

    def getOtherPluginApi(self, pluginName: str) -> Optional[object]:
        pluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = pluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.agent.PluginAgentEntryHookABC import (
            PluginAgentEntryHookABC,
        )

        assert isinstance(
            otherPlugin, PluginAgentEntryHookABC
        ), "Not an instance of PluginAgentEntryHookABC"

        return otherPlugin.publishedAgentApi

    @property
    def peekServerHttpPort(self) -> int:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.dataExchange.peekServerHttpPort

    @property
    def peekServerHost(self) -> str:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.dataExchange.peekServerHost

    @property
    def serviceId(self) -> str:
        import socket

        return "agent|" + socket.gethostname()

    @property
    def peekServerSSL(self) -> bool:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.dataExchange.peekServerUseSSL

    @property
    def peekServerSSLEnableMutualTLS(self) -> bool:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.dataExchange.peekServerSSLEnableMutualTLS
        )

    @property
    def peekServerSSLClientBundleFilePath(self) -> str:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.dataExchange.peekServerSSLClientBundleFilePath
        )

    @property
    def peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath(
        self,
    ) -> str:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.dataExchange.peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath
        )

    @property
    def peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath(self) -> str:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.dataExchange.peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath
        )

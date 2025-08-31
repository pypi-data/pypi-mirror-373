from pathlib import Path

from peek_plugin_base.worker.peek_worker_platform_hook_abc import (
    PeekWorkerPlatformHookABC,
)


class PeekWorkerPlatformHook(PeekWorkerPlatformHookABC):
    def getOtherPluginApi(self, pluginName: str):
        """Get Other Plugin API"""
        raise Exception("Workers don't share APIs")

    @property
    def serviceId(self) -> str:
        import socket

        return "worker|" + socket.gethostname()

    @property
    def fileStorageDirectory(self) -> Path:
        from peek_platform import PeekPlatformConfig

        return Path(PeekPlatformConfig.config.pluginDataPath(self._pluginName))

    @property
    def peekServerHttpPort(self) -> int:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.dataExchange.peekServerHttpPort

    @property
    def peekServerHost(self) -> str:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.dataExchange.peekServerHost

    @property
    def peekServerSSL(self) -> bool:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerUseSSL

    @property
    def peekServerSSLEnableMutualTLS(self) -> bool:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerSSLEnableMutualTLS

    @property
    def peekServerSSLClientBundleFilePath(self) -> str:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerSSLClientBundleFilePath

    @property
    def peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath(
        self,
    ) -> str:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath
        )

    @property
    def peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath(self) -> str:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.dataExchange.peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath
        )

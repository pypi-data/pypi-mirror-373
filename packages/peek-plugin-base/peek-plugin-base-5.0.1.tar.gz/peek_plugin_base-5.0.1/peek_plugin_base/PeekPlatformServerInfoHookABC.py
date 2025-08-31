from abc import ABCMeta, abstractmethod


class PeekPlatformServerInfoHookABC(metaclass=ABCMeta):
    """Peek Platform Server Info Hook

    This ABC provides information for plugins that want to connect to their own code
    running on the server service, via the inter peek service HTTP.

    """

    @property
    @abstractmethod
    def peekServerHttpPort(self) -> int:
        """Peek Server HTTP Port

        :return: The TCP Port of the Peek Servers HTTP Service (not the admin webapp site)
        """

    @property
    @abstractmethod
    def peekServerHost(self) -> str:
        """Peek Server Host

        :return: The IP address of the server where the peek server service is running.

        """

    @property
    @abstractmethod
    def peekServerSSL(self) -> bool:
        """Peek server https

        :return: true or false
        """

    @property
    @abstractmethod
    def peekServerSSLEnableMutualTLS(self) -> bool:
        """Peek server https with mTLS

        :return: true or false
        """

    @property
    @abstractmethod
    def peekServerSSLClientBundleFilePath(self) -> str:
        """PEM filepath that contains the key and the certificate of the tls
        client for mTLS

        :return: the PEM file path
        """

    @property
    @abstractmethod
    def peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath(
        self,
    ) -> str:
        """PEM filepath that contains certificate authorities used for mTLS to
         verify the identity of the peek server

        :return: the PEM file path
        """

    @property
    @abstractmethod
    def peekServerSSLMutualTLSTrustedPeerCertificateBundleFilePath(self) -> str:
        """PEM filepath that contains trusted peer certificates

        :return: the PEM file path
        """

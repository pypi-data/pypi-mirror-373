import logging
import os

from jsoncfg.config_classes import ConfigNode
from jsoncfg.functions import load_config

from peek_plugin_base.PeekVortexUtil import peekAgentName
from peek_plugin_base.PeekVortexUtil import peekFieldName
from peek_plugin_base.PeekVortexUtil import peekOfficeName
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.PeekVortexUtil import peekStorageName
from peek_plugin_base.PeekVortexUtil import peekWorkerName

logger = logging.getLogger(__name__)


class PluginPackageFileConfig:
    """
    This class helps with accessing the config for the plugin_package.json
    """

    def __init__(self, pluginRootDir: str):
        """
        Constructor

        :param pluginRootDir: The root directory of this package,
            where plugin_package.json lives.

        """
        self._pluginRoot = pluginRootDir
        if not os.path.isdir(self._pluginRoot):
            raise NotADirectoryError(self._pluginRoot)

        self._configFilePath = os.path.join(
            pluginRootDir, "plugin_package.json"
        )

        if not os.path.isfile(self._configFilePath):
            assert not os.path.exists(self._configFilePath)
            with open(self._configFilePath, "w") as fobj:
                fobj.write("{}")

        self._cfg = load_config(self._configFilePath)

    @property
    def config(self) -> ConfigNode:
        """Config

        :return: The jsoncfg config object, for accessing and saving the config.
        """
        return self._cfg

    def configForService(self, serviceName):
        if serviceName == peekStorageName:
            return self.config.storage

        if serviceName == peekFieldName:
            return self.config.field

        if serviceName == peekOfficeName:
            return self.config.office

        if serviceName == peekAgentName:
            return self.config.agent

        if serviceName == peekServerName:
            return self.config.logic

        if serviceName == peekWorkerName:
            return self.config.worker

        raise NotImplementedError()

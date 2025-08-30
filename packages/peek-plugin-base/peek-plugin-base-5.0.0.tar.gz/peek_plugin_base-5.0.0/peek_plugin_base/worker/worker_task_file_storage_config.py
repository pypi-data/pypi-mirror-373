import logging

logger = logging.getLogger(__name__)


def getWorkerPluginDataDir(pluginPackageName: str):
    # The config depends on the componentName, order is important
    from peek_worker_service.PeekWorkerConfig import PeekWorkerConfig

    return PeekWorkerConfig().pluginDataPath(pluginPackageName)

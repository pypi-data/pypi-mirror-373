import logging

from peek_plugin_base.PeekPlatformServerInfoHookABC import (
    PeekPlatformServerInfoHookABC,
)


logger = logging.getLogger(__name__)


def getLogicServiceHttpDetails() -> PeekPlatformServerInfoHookABC:
    # The config depends on the componentName, order is important
    from peek_worker_service.PeekWorkerConfig import PeekWorkerConfig

    return PeekWorkerConfig().dataExchange

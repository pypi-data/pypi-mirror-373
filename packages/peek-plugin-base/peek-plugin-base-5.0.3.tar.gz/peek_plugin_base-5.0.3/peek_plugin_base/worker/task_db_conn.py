import logging
from threading import Lock
from typing import Iterable
from typing import Optional

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

from peek_plugin_base.PeekVortexUtil import peekWorkerName
from peek_plugin_base.storage.DbConnection import _commonPrefetchDeclarativeIds

logger = logging.getLogger(__name__)


class TaskDbConn:
    _dbEngine = None
    _ScopedSession = None
    _sequenceMutex = Lock()

    @classmethod
    def getDbEngine(cls):

        if cls._dbEngine:
            return cls._dbEngine

        from peek_platform.file_config.PeekFileConfigABC import (
            PeekFileConfigABC,
        )
        from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import (
            PeekFileConfigSqlAlchemyMixin,
        )
        from peek_platform import PeekPlatformConfig

        class _WorkerTaskConfigMixin(
            PeekFileConfigABC, PeekFileConfigSqlAlchemyMixin
        ):
            pass

        PeekPlatformConfig.componentName = peekWorkerName

        _dbConnectString = _WorkerTaskConfigMixin().dbConnectString
        _dbEngineArgs = _WorkerTaskConfigMixin().dbEngineArgs
        cls._dbEngine = create_engine(_dbConnectString, **_dbEngineArgs)

        return cls._dbEngine

    @classmethod
    def getDbSession(cls):

        if not cls._ScopedSession:
            cls._ScopedSession = scoped_session(
                sessionmaker(bind=cls.getDbEngine())
            )

        return cls._ScopedSession()

    @classmethod
    def prefetchDeclarativeIds(
        cls, Declarative, count
    ) -> Optional[Iterable[int]]:
        """Prefetch Declarative IDs

        This function prefetches a chunk of IDs from a database sequence.
        Doing this allows us to preallocate the IDs before an insert, which significantly
        speeds up :

        * Orm inserts, especially those using inheritance
        * When we need the ID to assign it to a related object that we're also inserting.

        :param Declarative: The SQLAlchemy declarative class.
            (The class that inherits from DeclarativeBase)

        :param count: The number of IDs to prefetch

        :return: An iterable that dispenses the new IDs
        """
        return _commonPrefetchDeclarativeIds(
            cls.getDbEngine(), cls._sequenceMutex, Declarative, count
        )

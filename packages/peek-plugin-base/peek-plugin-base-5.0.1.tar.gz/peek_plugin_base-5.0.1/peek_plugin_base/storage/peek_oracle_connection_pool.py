import logging
from typing import Optional, Dict, Any, List, NamedTuple
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from twisted.internet import reactor

logger = logging.getLogger(__name__)


class PeekOracleConnectionDetails(NamedTuple):
    host: str
    username: str
    password: str
    port: int = 1521
    serviceName: str = "NMS"
    tnsName: Optional[str] = None


class PeekOracleConnectionPool:
    def __init__(
        self,
        connections: List[PeekOracleConnectionDetails],
        poolSize: int = 2,
        maxOverflow: int = 0,
    ):
        assert connections, "At least one connection detail must be provided"
        assert (
            len(connections) == 1
        ), "Currently only one connection is supported"

        self._connectionDetails = connections[0]
        self._poolSize = poolSize
        self._maxOverflow = maxOverflow
        self._oracleEngine: Optional = None
        self._oracleSessionCreator: Optional = None
        self._isConnected = False

    def connect(self, engineArgs: Optional[Dict[str, Any]] = None):
        if self._isConnected:
            logger.warning("Already connected to Oracle")
            return

        finalEngineArgs = self._getDefaultEngineArgs()
        if engineArgs:
            finalEngineArgs.update(engineArgs)

        if self._connectionDetails.tnsName:
            logger.debug(
                "Connecting to ORACLE %s as %s (pool_size=%d, max_overflow=%d)",
                self._connectionDetails.tnsName,
                self._connectionDetails.username,
                self._poolSize,
                self._maxOverflow,
            )
        else:
            logger.debug(
                "Connecting to ORACLE %s as %s (pool_size=%d, max_overflow=%d)",
                self._connectionDetails.host,
                self._connectionDetails.username,
                self._poolSize,
                self._maxOverflow,
            )

        dbUrl = self._buildDbUrl()
        self._oracleEngine = create_engine(dbUrl, **finalEngineArgs)
        self._oracleSessionCreator = scoped_session(
            sessionmaker(bind=self._oracleEngine)
        )

        self._registerShutdownCallback()

        self._isConnected = True
        if self._connectionDetails.tnsName:
            logger.info(
                "Successfully connected to ORACLE %s as %s",
                self._connectionDetails.tnsName,
                self._connectionDetails.username,
            )
        else:
            logger.info(
                "Successfully connected to ORACLE %s as %s",
                self._connectionDetails.host,
                self._connectionDetails.username,
            )

    def _getDefaultEngineArgs(self) -> Dict[str, Any]:
        return {
            "max_identifier_length": 128,
            "echo": False,
            "pool_size": self._poolSize,
            "max_overflow": self._maxOverflow,
            "pool_timeout": 60,
            "pool_recycle": 1800,
            "pool_pre_ping": True,
            "connect_args": {
                "encoding": "UTF-8",
                "nencoding": "UTF-8",
                "threaded": True,
            },
        }

    def _buildDbUrl(self) -> str:
        if self._connectionDetails.tnsName:
            return "oracle+cx_oracle://%s:%s@%s" % (
                self._connectionDetails.username,
                self._connectionDetails.password,
                self._connectionDetails.tnsName,
            )
        else:
            return "oracle+cx_oracle://%s:%s@%s:%d/%s" % (
                self._connectionDetails.username,
                self._connectionDetails.password,
                self._connectionDetails.host,
                self._connectionDetails.port,
                self._connectionDetails.serviceName,
            )

    def testAllConnections(self):
        """Test all possible pool connections"""
        if not self._isConnected:
            raise RuntimeError("Not connected to Oracle. Call connect() first.")

        maxConnections = self._poolSize + self._maxOverflow
        sessions = []

        try:
            for i in range(maxConnections):
                session = self._oracleSessionCreator()
                result = session.execute(
                    text("SELECT 'Oracle connection test' FROM DUAL")
                )
                sessions.append(session)
                logger.debug(
                    f"Connection {i + 1}/{maxConnections}: {result.scalar()}"
                )

            logger.info(
                f"Successfully tested all {maxConnections} pool connections"
            )

        except Exception as e:
            logger.error(
                f"Failed to create connection {len(sessions) + 1}/{maxConnections}: {e}"
            )
            raise

        finally:
            for session in sessions:
                session.close()

    def _registerShutdownCallback(self):
        def closePoolOnShutdown():
            logger.info("Reactor stopping, closing Oracle connection pool")
            self.dispose()

        reactor.addSystemEventTrigger("before", "shutdown", closePoolOnShutdown)

    @property
    def engine(self):
        if not self._isConnected:
            raise RuntimeError("Not connected to Oracle. Call connect() first.")
        return self._oracleEngine

    @property
    def sessionCreator(self):
        if not self._isConnected:
            raise RuntimeError("Not connected to Oracle. Call connect() first.")
        return self._oracleSessionCreator

    @property
    def isConnected(self) -> bool:
        return self._isConnected

    @contextmanager
    def session(self):
        """Context manager for database sessions"""
        if not self._isConnected:
            raise RuntimeError("Not connected to Oracle. Call connect() first.")

        session = self._oracleSessionCreator()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def testConnection(self) -> bool:
        """Test a single connection without full pool testing"""
        try:
            with self.session() as session:
                result = session.execute(
                    text("SELECT 'Connection test' FROM DUAL")
                )
                logger.debug(f"Connection test result: {result.scalar()}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def dispose(self):
        if self._oracleEngine:
            logger.debug("Disposing Oracle connection pool")
            self._oracleEngine.dispose()
            self._oracleEngine = None
        self._oracleSessionCreator = None
        self._isConnected = False
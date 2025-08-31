import logging
import traceback
from textwrap import dedent
from threading import Lock
from typing import Optional, Dict, Union, Callable, Iterable, NamedTuple

from vortex.DeferUtil import isMainThread

from peek_plugin_base.storage.AlembicEnvBase import (
    ensureSchemaExists,
    isMssqlDialect,
    isPostGreSQLDialect,
)
from pytmpdir.directory_ import Directory
from sqlalchemy import create_engine, Integer, text
from sqlalchemy.types import SmallInteger, BigInteger
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.schema import MetaData, Sequence
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)

DbSessionCreator = Callable[[], Session]

DelcarativeIdGen = Optional[Iterable[int]]
DeclarativeIdCreator = Callable[[object, int], DelcarativeIdGen]


class _Column(NamedTuple):
    columnName: str
    isColumnTypeIntLike: bool


def _non_indexed_foreign_keys(metadata, engine=None):
    """
    Finds all non indexed foreign keys from all tables of given MetaData.

    Very useful for optimizing postgresql database and finding out which
    foreign keys need indexes.

    :param metadata: MetaData object to inspect tables from
    """
    reflected_metadata = MetaData()

    bind = getattr(metadata, "bind", None)
    if bind is None and engine is None:
        raise Exception(
            "Either pass a metadata object with bind or "
            "pass engine as a second parameter"
        )

    constraints = defaultdict(list)

    for table_name in metadata.tables.keys():
        table = Table(
            table_name, reflected_metadata, autoload_with=bind or engine
        )

        for constraint in table.constraints:
            if not isinstance(constraint, ForeignKeyConstraint):
                continue

            if not has_index(constraint):
                constraints[table.name].append(constraint)

    return dict(constraints)


class DbConnection:
    def __init__(
        self,
        dbConnectString: str,
        metadata: MetaData,
        alembicDir: str,
        dbEngineArgs: Optional[Dict[str, Union[str, int]]] = None,
        enableForeignKeys=False,
        enableCreateAll=True,
    ):
        """SQLAlchemy Database Connection

        This class takes care of migrating the database and establishing thing database
        connections and ORM sessions.

        :param dbConnectString:
            The connection string for the DB.
            See http://docs.sqlalchemy.org/en/latest/core/engines.html

        :param metadata:
            The instance of the metadata for this connection,
            This is schema qualified MetaData(schema="schama_name")

        :param alembicDir:
            The absolute location of the alembic directory (versions dir lives under this)

        :param dbEngineArgs:
            The arguments to pass to the database engine, See
            http://docs.sqlalchemy.org/en/latest/core/engines.html#engine-creation-api

        :param enableCreateAll:
            If the schema doesn't exist, then the migration is allowed
            to use matadata.create_all()

        :param enableForeignKeys:
            Perform a check to ensure foriegn keys have indexes after the db is
            migrated and connected.
        """
        self._dbConnectString = dbConnectString
        self._metadata = metadata
        self._alembicDir = alembicDir

        self._dbEngine = None
        self._ScopedSession = None
        self._dbEngineArgs = (
            dbEngineArgs
            if dbEngineArgs
            else {
                "client_encoding": "utf8",
                "echo": False,
                "max_overflow": 50,
                "pool_recycle": 3540,
                "pool_size": 5,
                "pool_timeout": 60,
            }
        )

        self._sequenceMutex = Lock()

        self._enableForeignKeys = enableForeignKeys
        self._enableCreateAll = enableCreateAll

    def closeAllSessions(self):
        """Close All Session

        Close all ORM sessions connected to this DB engine.

        """
        self.ormSessionCreator()  # Ensure we have a session maker and session
        self._ScopedSession.close_all()

    @property
    def ormSessionCreator(self) -> DbSessionCreator:
        sessionCreator = self.__ormSessionCreator

        def call():
            if isMainThread():
                logger.exception(
                    "This plugin has called"
                    " SQLAlchemy code in the main thread,"
                    " this is very bad"
                )

            return sessionCreator()

        return call

    @property
    def __ormSessionCreator(self) -> DbSessionCreator:
        """Get Orm Session

        :return: A SQLAlchemy session scoped for the callers thread..
        """
        assert self._dbConnectString

        if self._ScopedSession:
            return self._ScopedSession

        self._ScopedSession = scoped_session(sessionmaker(bind=self.dbEngine))

        return self._ScopedSession

    @property
    def dbEngine(self) -> Engine:
        """Get DB Engine

        This is not thread safe, use the ormSesson to execute SQL statements instead.
        self.ormSession.execute(...)

        :return: the DB Engine used to connect to the database.

        """
        if self._dbEngine is None:
            self._dbEngine = create_engine(
                self._dbConnectString, **self._dbEngineArgs
            )

        return self._dbEngine

    def migrate(self) -> None:
        """Migrate

        Perform a database migration, upgrading to the latest schema level.
        """
        assert self.ormSessionCreator, "ormSessionCreator is not defined"

        connection = self._dbEngine.connect()
        isDbInitialised = self._dbEngine.dialect.has_table(
            connection, "alembic_version", schema=self._metadata.schema
        )
        connection.close()

        if isDbInitialised or not self._enableCreateAll:
            self._doMigration(self._dbEngine)

        else:
            self._doCreateAll(self._dbEngine)

        if self._enableForeignKeys:
            self.checkForeignKeys(self._dbEngine)

    def checkForeignKeys(self, engine: Engine) -> None:
        """Check Foreign Keys

        Log any foreign keys that don't have indexes assigned to them.
        This is a performance issue.

        """
        missing = _non_indexed_foreign_keys(self._metadata, engine=engine)

        for table, keys in missing.items():
            for key in keys:
                logger.warning("Missing index on ForeignKey %s" % key.columns)

    @deferToThreadWrapWithLogger(logger)
    def prefetchDeclarativeIds(self, Declarative, count) -> DelcarativeIdGen:
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
            self.dbEngine, self._sequenceMutex, Declarative, count
        )

    def _runAlembicCommand(self, command, *args):
        configFile = self._writeAlembicIni()

        from alembic.config import Config

        alembic_cfg = Config(configFile.name)
        command(alembic_cfg, *args)

    def _doCreateAll(self, engine):
        ensureSchemaExists(engine, self._metadata.schema)
        self._metadata.create_all(engine)

        from alembic import command

        self._runAlembicCommand(command.stamp, "head")

    def _writeAlembicIni(self):
        cfg = """
        [alembic]
        script_location = %(alembicDir)s

        sourceless = true
        sqlalchemy.url = %(url)s

        [alembic:exclude]
        tables = spatial_ref_sys

        [logging]
        default_level = INFO
        """
        cfg = dedent(cfg)

        cfg %= {"alembicDir": self._alembicDir, "url": self._dbConnectString}

        dir = Directory()
        file = dir.createTempFile()

        with file.open(write=True, asBin=False) as f:
            f.write(cfg)

        return file.namedTempFileReader()

    def _doMigration(self, engine):
        ensureSchemaExists(engine, self._metadata.schema)

        from alembic import command

        self._runAlembicCommand(command.upgrade, "head")


def convertToCoreSqlaInsert(ormObj, Declarative):
    insertDict = dict()

    for fieldName in Declarative.tupleFieldNames():
        value = getattr(ormObj, fieldName)

        if value is None:
            Col = getattr(Declarative, fieldName)
            if isinstance(Col, InstrumentedAttribute):
                value = Col.server_default.arg if Col.server_default else None
                if value == "false":
                    value = False

                elif value == "true":
                    value = True

        insertDict[fieldName] = value

    return insertDict


def pgCopyInsert(rawConn, table, inserts):
    sortedColumns = []
    for column in table.columns:
        isColumnTypeIntLike = False
        if (
            isinstance(column.type, Integer)
            or isinstance(column.type, SmallInteger)
            or isinstance(column.type, BigInteger)
        ):
            isColumnTypeIntLike = True
        col = _Column(
            columnName=column.name, isColumnTypeIntLike=isColumnTypeIntLike
        )
        sortedColumns.append(col)

    sortedColumns.sort(key=lambda c: c.columnName)

    cursor = rawConn.cursor()
    tableName = f'{table.schema}."{table.name}"'

    sortedColumnNameStr = ", ".join(
        [f'"{c.columnName}"' for c in sortedColumns]
    )

    q = f"COPY {tableName} ({sortedColumnNameStr}) FROM STDIN"

    with cursor.copy(q) as copy:
        for insert in inserts:
            row = []

            for column in sortedColumns:
                columnValue = insert.get(column.columnName, None)

                if columnValue is not None and column.isColumnTypeIntLike:
                    columnValue = int(columnValue)

                row.append(columnValue)

            copy.write_row(row)

    cursor.close()


def _commonPrefetchDeclarativeIds(
    engine, mutex, Declarative, count
) -> Optional[Iterable[int]]:
    """Common Prefetch Declarative IDs

    This function is used by the worker and server
    """
    if not count:
        logger.debug("Count was zero, no range returned")
        return

    conn = engine.connect()
    transaction = conn.begin()
    mutex.acquire()
    try:
        sequence = Sequence(
            "%s_id_seq" % Declarative.__tablename__,
            schema=Declarative.metadata.schema,
        )

        if isPostGreSQLDialect(engine):
            sql = "SELECT setval('%(seq)s', (select nextval('%(seq)s') + %(add)s), true)"
            sql %= {
                "seq": '"%s"."%s"' % (sequence.schema, sequence.name),
                "add": count,
            }
            nextStartId = conn.execute(text(sql)).fetchone()[0]
            startId = nextStartId - count

        elif isMssqlDialect(engine):
            startId = (
                conn.execute(
                    'SELECT NEXT VALUE FOR "%s"."%s"'
                    % (sequence.schema, sequence.name)
                ).fetchone()[0]
                + 1
            )

            nextStartId = startId + count

            conn.execute(
                'alter sequence "%s"."%s" restart with %s'
                % (sequence.schema, sequence.name, nextStartId)
            )

        else:
            raise NotImplementedError()

        transaction.commit()

        return iter(range(startId, nextStartId))

    finally:
        mutex.release()
        conn.close()

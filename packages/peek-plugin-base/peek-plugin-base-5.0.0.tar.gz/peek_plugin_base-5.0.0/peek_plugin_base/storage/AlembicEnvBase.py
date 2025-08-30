import logging
from alembic import context
from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.dialects.postgresql.base import PGDialect

log = logging.getLogger(__name__)


def isMssqlDialect(engine):
    return isinstance(engine.dialect, MSDialect)


def isPostGreSQLDialect(engine):
    return isinstance(engine.dialect, PGDialect)


def ensureSchemaExists(engine, schemaName):
    # Ensure the schema exists
    with engine.connect() as conn:
        if isinstance(conn.dialect, MSDialect):
            if (
                list(conn.execute(text("SELECT SCHEMA_ID('%s')" % schemaName)))[
                    0
                ][0]
                is None
            ):
                conn.execute(text("CREATE SCHEMA [%s]" % schemaName))
                conn.commit()
        elif isinstance(conn.dialect, PGDialect):
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS "%s" ' % schemaName))
            conn.commit()
        else:
            raise Exception("unknown dialect %s" % conn.dialect)


class AlembicEnvBase:
    def __init__(self, targetMetadata):
        from peek_platform.util.LogUtil import setupPeekLogger

        setupPeekLogger()
        self._config = context.config
        self._targetMetadata = targetMetadata
        self._schemaName = targetMetadata.schema

    def _includeObjectFilter(self, object, name, type_, reflected, compare_to):
        # If it's not in this schema, don't include it
        if hasattr(object, "schema") and object.schema != self._schemaName:
            return False
        return True

    def run(self):
        """Run migrations in 'online' mode.
        In this scenario we need to create an Engine
        and associate a connection with the context.
        """
        connectable = engine_from_config(
            self._config.get_section(self._config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            client_encoding="utf8",
        )
        with connectable.connect() as connection:
            ensureSchemaExists(connectable, self._schemaName)
            log.info("Migrating Peek schema %s" % self._schemaName)
            schemaWiseConnection = connection.execution_options(
                schema_translate_map={None: self._schemaName}
            )
            context.configure(
                connection=schemaWiseConnection,
                target_metadata=self._targetMetadata,
                include_object=self._includeObjectFilter,
                include_schemas=False,
                # process_revision_directives=self._process_revision_directives,
                version_table_schema=self._schemaName,
            )
            # schema-wise transactions
            with context.begin_transaction():
                context.run_migrations()

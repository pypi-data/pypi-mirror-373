import time
from unittest import TestCase

import sqlalchemy
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    SmallInteger,
    Table,
    BigInteger,
)

from storage.DbConnection import pgCopyInsert


def _pgCopyInsertOld(rawConn, table, inserts):
    colTypes = [c.type for c in table.c]

    def convert(index, val):
        if val is None:
            return "\\N"

        if isinstance(colTypes[index], Integer):
            return str(val).split(".")[0]

        return (
            str(val)
            .replace("\\", "\\\\")
            .replace("\t", "\\t")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )

    sortedColumnNames = table.columns.keys()
    sortedColumnNames.sort()

    cursor = rawConn.cursor()
    tableName = f'{table.schema}."{table.name}"'

    sortedColumnNameStr = ", ".join([f'"{c}"' for c in sortedColumnNames])

    q = f"COPY {tableName} ({sortedColumnNameStr}) FROM STDIN"

    with cursor.copy(q) as copy:
        for insert in inserts:
            row = []

            for columnName in sortedColumnNames:
                columnValue = insert.get(columnName, None)
                columnType = table.columns[columnName].type

                if columnValue is not None and (
                    isinstance(columnType, Integer)
                    or isinstance(columnType, SmallInteger)
                    or isinstance(columnType, BigInteger)
                ):
                    columnValue = int(columnValue)

                row.append(columnValue)

            copy.write_row(row)

    cursor.close()


class TestPgCopyInsert(TestCase):
    def setUp(self):
        # create a table for testing
        self.metadata = MetaData()

        self.tableName = "_TestPgCopyInsert"

        self.testTable = Table(
            self.tableName,
            self.metadata,
            Column("field1", Integer),
            Column("field2", SmallInteger),
            Column("field3", BigInteger),
            schema="core_user",
        )

        engineArgs = {
            "client_encoding": "utf8",
            "echo": False,
            "max_overflow": 50,
            "pool_recycle": 600,
            "pool_size": 20,
            "pool_timeout": 60,
        }

        self.engine = sqlalchemy.create_engine(
            "postgresql+psycopg://peek:PASSWORD@127.0.0.1/peek", **engineArgs
        )

        self.conn = self.engine.raw_connection()

        self.metadata.bind = self.engine
        self.metadata.drop_all(bind=self.engine)
        self.metadata.create_all(bind=self.engine)

    def tearDown(self):
        self.conn.close()
        self.metadata.drop_all(bind=self.engine)

    def testTransaction(self):
        inserts = [
            {"field1": 2, "field2": 3, "field3": 4},
            {"field1": 5, "field2": 6, "field3": 7},
        ]

        pgCopyInsert(self.conn, self.testTable, inserts)
        self.conn.commit()

        # Now read the data and verify it's correctly inserted
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM core_user."{self.tableName}"')
        result = cur.fetchall()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (2, 3, 4))
        self.assertEqual(result[1], (5, 6, 7))

        self.conn.rollback()

        cur.close()

    def testPerformance(self):
        inserts = [
            {"field1": 2, "field2": 3, "field3": 4},
        ]

        nRows = 10_000_000

        inserts = inserts * nRows

        start = time.monotonic()
        pgCopyInsert(self.conn, self.testTable, inserts)
        self.conn.commit()
        end = time.monotonic()
        print(
            f"{nRows} rows of insert with enhancement "
            f"took {end-start:1.03f}s"
        )

        start = time.monotonic()
        _pgCopyInsertOld(self.conn, self.testTable, inserts)
        self.conn.commit()
        end = time.monotonic()
        print(
            f"{nRows} rows of insert with no enhancement "
            f"took {end-start:1.03f}s"
        )

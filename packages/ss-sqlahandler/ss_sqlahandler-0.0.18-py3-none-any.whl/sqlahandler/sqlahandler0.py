"""
Created on 27 May 2025

@author: ph1jb
"""

from configargparse import Namespace  # type: ignore
from pandas.core.frame import DataFrame
from pandas.io.sql import SQLTable
from sqlalchemy.dialects.mysql.dml import insert
from sqlalchemy.engine import Result, Row, URL
from sqlalchemy.sql.base import Executable
from types import SimpleNamespace
from typing import cast, Sequence, Dict
from typing_extensions import TypedDict
import logging
import pandas
import sqlalchemy

# import pandas as pd


class MysqlOptions(TypedDict):
    user: str
    password: str
    host: str
    port: int
    database: str


class SqlalchemyOptions(TypedDict):
    username: str
    password: str
    host: str
    port: int
    database: str


logger = logging.getLogger(__name__)


class SqlaHandler:
    """Import DataFrames into a SQL database."""

    def __init__(self, engine: sqlalchemy.Engine):
        self.engine = engine

    @staticmethod
    def get_mysql_overrides(config: SimpleNamespace) -> MysqlOptions:
        """Get MySQL overrides from config.
        config.mysql_database, config.mysql_host, ...
        returns: {'database':database, 'host':host, 'password':password, 'user':user, ...}
        """
        mysql_keys = ("database", "host", "password", "user")
        return cast(
            MysqlOptions,
            {k: getattr(config, f"mysql_{k}") for k in mysql_keys if getattr(config, f"mysql_{k}")},
        )

    @staticmethod
    def get_sqla_options(
        mysql_options: MysqlOptions, mysql_overrides: MysqlOptions
    ) -> SqlalchemyOptions:
        """Get SSQL Alchemy options from MySQL options and MySQL overrides.
        mysql_options: {"mysql_database": "database","mysql_host": "host",...}
        mysql_overrides: {"mysql_database": "database","mysql_host": "host",...}
        """
        mysql_options2 = mysql_options.copy()
        mysql_options2.update(mysql_overrides)
        d = {**mysql_options2}  # Lose type
        d["username"] = d.pop("user")  # Rename key
        return cast(SqlalchemyOptions, d)

    @staticmethod
    def get_sqla_url(sqla_options: SqlalchemyOptions, drivername="mysql+mysqlconnector") -> URL:
        """Get sqlalchemy URL object (used in create_engine) from sqla_options.
        sqla_options: {"database": "database", ... "username": "username",}
        appends other options to ?query parameter
        """
        sqlalchemy_keys = ("username", "password", "host", "port", "database")
        query = {k: str(v) for (k, v) in sqla_options.items() if k not in sqlalchemy_keys}
        sqla_options2 = cast(
            SqlalchemyOptions, {k: v for (k, v) in sqla_options.items() if k in sqlalchemy_keys}
        )
        return URL.create(drivername, **sqla_options2, query=query)

    def execute(self, statement: Executable, **kwargs) -> Result:
        """Execute a SQL statement return any values."""
        logger.debug("Executing %(statement)s", {"statement": statement})
        with self.engine.connect() as connection:
            result = connection.execute(statement, **kwargs)
            connection.commit()
        logger.debug("Executed %(statement)s", {"statement": statement})
        return result

    def fetchall(self, statement, **kwargs) -> Sequence[Row]:
        """Execute a SQL select statement, return all rows."""
        return self.execute(statement, **kwargs).all()

    def fetchfirst(self, statement: Executable, **kwargs) -> Row | None:
        """Execute an SQL statement, return first row."""
        return self.execute(statement, **kwargs).first()

    def fetchone(self, statement: Executable, **kwargs) -> Row:
        """Execute an SQL statement, return a single row (raise exception if n rows <> 1."""
        return self.execute(statement, **kwargs).one()

    def read_sql(self, table: str | sqlalchemy.Selectable, **kwargs) -> DataFrame:
        """Select rows from database table into pandas DataFrame."""
        logger.debug("Selecting from table %(table)s", {"table": table})
        with self.engine.connect() as connection:
            if "chunksize" in kwargs.keys():
                df = pandas.concat(pandas.read_sql(table, connection, **kwargs))  # type: ignore
            else:
                df = pandas.read_sql(table, connection, **kwargs)  # type: ignore
        logger.debug("Selected from table %(table)s", {"table": table})
        return df

    def read_sql_query(self, statement: sqlalchemy.Selectable, **kwargs) -> DataFrame:
        """Select rows from database table into pandas DataFrame."""
        logger.debug("Querying %(statement)s", {"statement": statement})
        with self.engine.connect() as connection:
            if "chunksize" in kwargs.keys():
                df = pandas.concat(pandas.read_sql_query(statement, connection, **kwargs))  # type: ignore
            else:
                df = pandas.read_sql_query(statement, connection, **kwargs)  # type: ignore
        logger.debug("Queried %(statement)s", {"statement": statement})
        return df

    def read_sql_table(self, table: str, **kwargs) -> DataFrame:
        """Select rows from database table into pandas DataFrame."""
        logger.debug("Selecting from table %(table)s", {"table": table})
        with self.engine.connect() as connection:
            if "chunksize" in kwargs.keys():
                df = pandas.concat(chunk for chunk in pandas.read_sql_table(table, connection, **kwargs))  # type: ignore
            else:
                df = pandas.read_sql_table(table, connection, **kwargs)  # type: ignore
        logger.debug("Selected from table %(table)s", {"table": table})
        return df

    def to_sql(self, df: DataFrame, table: str, **kwargs):
        """Insert a pandas DataFrame into a database table.
        # chunksize to avoid exceeding the SQL max_packet size. (MCS data files are large.)
        """
        nrows = len(df.index)
        logger.debug(
            "Inserting %(nrows)s rows into table: %(table)s",
            {"nrows": nrows, "table": table},
        )
        df.to_sql(table, self.engine, **kwargs)
        logger.debug(
            "Inserted %(nrows)s rows into table: %(table)s",
            {"nrows": nrows, "table": table},
        )

    @staticmethod
    def upsert(table: SQLTable, conn, keys, data_iter):
        """Method used by to_sql to do: SQL insert on duplicate key update
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html"""
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data)
        columns = keys[1:]
        d = {col: getattr(stmt.inserted, col) for col in columns}
        stmt = stmt.on_duplicate_key_update(**d)
        result = conn.execute(stmt)
        return result.rowcount

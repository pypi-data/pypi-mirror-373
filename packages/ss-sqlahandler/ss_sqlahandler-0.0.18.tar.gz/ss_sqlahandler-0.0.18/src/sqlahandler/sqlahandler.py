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
from typing import cast, Sequence
from typing_extensions import TypedDict
import logging
import pandas
import sqlalchemy


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
    """Handles interaction between pandas DataFrames and an SQL database using SQLAlchemy."""

    def __init__(self, engine: sqlalchemy.Engine):
        """
        Initialize the SqlaHandler.
        :param engine: SQLAlchemy engine to use for database connections.
        """
        self.engine = engine

    @staticmethod
    def _create_sqlahandler(config: Namespace):
        """Create an instance of SqlaHandler."""
        mysql_overrides = SqlaHandler.get_mysql_overrides(config)
        sqla_options = SqlaHandler.get_sqla_options(config.mysql_options, mysql_overrides)
        drivername = "mysql" if (config.connector == "mysqlclient") else f"mysql+{config.connector}"
        sqla_url = SqlaHandler.get_sqla_url(sqla_options, drivername=drivername)
        engine = sqlalchemy.create_engine(sqla_url)
        logger.debug("Database connection string: %s", engine)
        return SqlaHandler(engine)

    @staticmethod
    def get_mysql_overrides(config: SimpleNamespace) -> MysqlOptions:
        """
        Extract MySQL connection overrides from the config object.

        :param config: Configuration namespace with mysql_* attributes.
        :return: Dictionary with keys 'user', 'password', 'host', 'database'.
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
        """
        Merge default MySQL options with overrides and adapt them for SQLAlchemy.

        :param mysql_options: Default MySQL connection options.
        :param mysql_overrides: Overridden MySQL options.
        :return: SQLAlchemy-compatible options dictionary.
        """
        mysql_options2 = mysql_options.copy()
        mysql_options2.update(mysql_overrides)
        d = {**mysql_options2}
        d["username"] = d.pop("user")
        return cast(SqlalchemyOptions, d)

    @staticmethod
    def get_sqla_url(
        sqla_options: SqlalchemyOptions, drivername: str = "mysql+mysqlconnector"
    ) -> URL:
        """
        Construct a SQLAlchemy connection URL.

        :param sqla_options: SQLAlchemy connection options.
        :param drivername: SQLAlchemy dialect+driver string.
        :return: SQLAlchemy URL object.
        """
        sqlalchemy_keys = ("username", "password", "host", "port", "database")
        query = {k: str(v) for (k, v) in sqla_options.items() if k not in sqlalchemy_keys}
        sqla_options2 = cast(
            SqlalchemyOptions, {k: v for (k, v) in sqla_options.items() if k in sqlalchemy_keys}
        )
        return URL.create(drivername, **sqla_options2, query=query)

    def execute(self, statement: Executable, **kwargs) -> Result:
        """
        Execute a SQL statement.

        :param statement: SQL statement to execute.
        :param kwargs: Additional arguments passed to `execute()`.
        :return: SQLAlchemy Result object.
        """
        logger.debug("Executing %(statement)s", {"statement": statement})
        with self.engine.connect() as connection:
            result = connection.execute(statement, **kwargs)
            connection.commit()
        logger.debug("Executed %(statement)s", {"statement": statement})
        return result

    def fetchall(self, statement: Executable, **kwargs) -> Sequence[Row]:
        """
        Execute a SELECT statement and return all rows.

        :param statement: SQL SELECT statement.
        :param kwargs: Additional arguments passed to `execute()`.
        :return: List of rows.
        """
        return self.execute(statement, **kwargs).all()

    def fetchfirst(self, statement: Executable, **kwargs) -> Row | None:
        """
        Execute a SELECT statement and return the first row.

        :param statement: SQL SELECT statement.
        :param kwargs: Additional arguments passed to `execute()`.
        :return: First row, or None if no results.
        """
        return self.execute(statement, **kwargs).first()

    def fetchone(self, statement: Executable, **kwargs) -> Row:
        """
        Execute a SELECT statement and return exactly one row.

        :param statement: SQL SELECT statement.
        :param kwargs: Additional arguments passed to `execute()`.
        :return: Single row.
        :raises: sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound
        """
        return self.execute(statement, **kwargs).one()

    def read_sql(self, table: str | sqlalchemy.Selectable, **kwargs) -> DataFrame:
        """
        Read a SQL table or SELECT query into a pandas DataFrame.

        :param table: Table name or SQL SELECT expression.
        :param kwargs: Additional arguments passed to `pandas.read_sql()`.
        :return: DataFrame with results.
        """
        logger.debug("Selecting from table %(table)s", {"table": table})
        with self.engine.connect() as connection:
            if "chunksize" in kwargs:
                df = pandas.concat(pandas.read_sql(table, connection, **kwargs))  # type: ignore
            else:
                df = pandas.read_sql(table, connection, **kwargs)  # type: ignore
        logger.debug("Selected from table %(table)s", {"table": table})
        return df

    def read_sql_query(self, statement: sqlalchemy.Selectable, **kwargs) -> DataFrame:
        """
        Read the results of a SQL query into a pandas DataFrame.

        :param statement: SQL SELECT expression.
        :param kwargs: Additional arguments passed to `pandas.read_sql_query()`.
        :return: DataFrame with results.
        """
        logger.debug("Querying %(statement)s", {"statement": statement})
        with self.engine.connect() as connection:
            if "chunksize" in kwargs:
                df = pandas.concat(pandas.read_sql_query(statement, connection, **kwargs))  # type: ignore
            else:
                df = pandas.read_sql_query(statement, connection, **kwargs)  # type: ignore
        logger.debug("Queried %(statement)s", {"statement": statement})
        return df

    def read_sql_table(self, table: str, **kwargs) -> DataFrame:
        """
        Read an entire SQL table into a pandas DataFrame.

        :param table: Table name.
        :param kwargs: Additional arguments passed to `pandas.read_sql_table()`.
        :return: DataFrame with table contents.
        """
        logger.debug("Selecting from table %(table)s", {"table": table})
        with self.engine.connect() as connection:
            if "chunksize" in kwargs:
                df = pandas.concat(chunk for chunk in pandas.read_sql_table(table, connection, **kwargs))  # type: ignore
            else:
                df = pandas.read_sql_table(table, connection, **kwargs)  # type: ignore
        logger.debug("Selected from table %(table)s", {"table": table})
        return df

    def to_sql(self, df: DataFrame, table: str, **kwargs) -> None:
        """
        Write a DataFrame to a SQL table.

        :param df: DataFrame to insert.
        :param table: Target table name.
        :param kwargs: Additional arguments passed to `DataFrame.to_sql()`.
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
    def upsert(table: SQLTable, conn, keys: Sequence[str], data_iter) -> int:
        """
        Perform an "upsert" (INSERT ... ON DUPLICATE KEY UPDATE) using SQLAlchemy.

        :param table: SQLAlchemy SQLTable object.
        :param conn: Active database connection.
        :param keys: Column names for the insert.
        :param data_iter: Iterable of row values (tuples).
        :return: Number of affected rows.
        """
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data)
        columns = keys[1:]
        d = {col: getattr(stmt.inserted, col) for col in columns}
        stmt = stmt.on_duplicate_key_update(**d)
        result = conn.execute(stmt)
        return result.rowcount

"""
Created on 17 July 2025

@author: ph1jb
"""

from pandas.testing import assert_frame_equal
from sqlahandler import SqlaHandler
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, insert, select
from sqlalchemy.engine import URL
from types import SimpleNamespace
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def sqlite_engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def sqlahandler(sqlite_engine):
    return SqlaHandler(sqlite_engine)


@pytest.fixture(scope="function")
def setup_table(sqlite_engine):
    meta = MetaData()
    test_table = Table(
        "test_table",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", String),
    )
    meta.create_all(sqlite_engine)
    yield test_table
    meta.drop_all(sqlite_engine)


class TestStaticMethods:
    def test_get_mysql_overrides(self):
        config = SimpleNamespace(
            mysql_database="mydb",
            mysql_host="localhost",
            mysql_user="admin",
            mysql_password="secret",
        )
        result = SqlaHandler.get_mysql_overrides(config)
        assert result == {
            "database": "mydb",
            "host": "localhost",
            "user": "admin",
            "password": "secret",
        }

    def test_get_sqla_options(self):
        mysql_options = {
            "user": "admin",
            "password": "secret",
            "host": "localhost",
            "database": "mydb",
        }
        mysql_overrides = {"user": "admin_overridden", "host": "localhost_overridden"}
        result = SqlaHandler.get_sqla_options(mysql_options, mysql_overrides)
        expected = {
            "username": "admin_overridden",  # Note usename not user
            "password": "secret",
            "host": "localhost_overridden",
            "database": "mydb",
        }
        assert result == expected

    def test_get_sqla_url(self):
        sqla_options = {
            "username": "admin",
            "password": "secret",
            "host": "localhost",
            "port": 3306,
            "database": "mydb",
            "charset": "utf8",
        }
        url = SqlaHandler.get_sqla_url(sqla_options, drivername="sqlite")
        assert isinstance(url, URL)
        assert str(url) == "sqlite://admin:***@localhost:3306/mydb?charset=utf8"
        assert url.password == "secret"


class TestExecution:
    def test_execute_and_fetch(self, sqlahandler, setup_table):
        # Arrange
        statement = insert(setup_table).values(id=1, name="Alice")
        # Act
        sqlahandler.execute(statement)
        # Assert
        statement = select(setup_table)
        rows = sqlahandler.fetchall(statement)
        expected = [(1, "Alice")]
        assert rows == expected

    def test_fetchall(self, sqlahandler, setup_table):
        # Arrange
        statement = insert(setup_table).values(
            [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Cath"}]
        )
        # Act
        sqlahandler.execute(statement)
        # Assert
        statement = select(setup_table)
        sqlahandler.execute(statement)
        row = sqlahandler.fetchall(statement)
        expected = [(2, "Bob"), (3, "Cath")]
        assert row == expected

    def test_fetchfirst(self, sqlahandler, setup_table):
        # Arrange
        statement = insert(setup_table).values(
            [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Cath"}]
        )
        # Act
        sqlahandler.execute(statement)
        # Assert
        statement = select(setup_table)
        sqlahandler.execute(statement)
        row = sqlahandler.fetchfirst(statement)
        expected = (2, "Bob")
        assert row == expected

    def test_fetchone(self, sqlahandler, setup_table):
        # Arrange
        statement = insert(setup_table).values(id=2, name="Bob")
        # Act
        sqlahandler.execute(statement)
        # Assert
        statement = select(setup_table)
        sqlahandler.execute(statement)
        row = sqlahandler.fetchone(statement)
        expected = (2, "Bob")
        assert row == expected

    def test_fetchone_exception(self, sqlahandler, setup_table):
        """Fetch one: query returns <>1 row so raises exception."""
        # Assert
        statement = select(setup_table)
        sqlahandler.execute(statement)
        with pytest.raises(Exception):
            sqlahandler.fetchone(statement)


class TestDataFrameOperations:
    @pytest.mark.parametrize("kwargs", [{}, {"chunksize": 1}])
    def test_to_sql_and_read_sql(self, sqlahandler, kwargs):
        df_original = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        sqlahandler.to_sql(df_original, "df_table", if_exists="replace", index=False)
        df_read = (
            sqlahandler.read_sql("df_table", **kwargs).sort_values("id").reset_index(drop=True)
        )
        assert_frame_equal(df_read, df_original)

    @pytest.mark.parametrize("kwargs", [{}, {"chunksize": 1}])
    def test_read_sql_query(self, sqlahandler, kwargs):
        df_original = pd.DataFrame({"id": [1], "name": ["Clara"]})
        sqlahandler.to_sql(df_original, "query_table", if_exists="replace", index=False)

        df_query = (
            sqlahandler.read_sql_query("SELECT * FROM query_table", **kwargs)
            .sort_values("id")
            .reset_index(drop=True)
        )
        assert_frame_equal(df_query, df_original)

    @pytest.mark.parametrize("kwargs", [{}, {"chunksize": 1}])
    def test_read_sql_table(self, sqlahandler, kwargs):
        df_original = pd.DataFrame({"id": [1], "name": ["Dan"]})
        sqlahandler.to_sql(df_original, "table_table", if_exists="replace", index=False)

        df_table = (
            sqlahandler.read_sql_table("table_table", **kwargs)
            .sort_values("id")
            .reset_index(drop=True)
        )
        assert_frame_equal(df_table, df_original)


class TestUpsert:
    @pytest.mark.skip("sqlite3 does not support upsert")
    def test_upsert(self, mocker):
        """Skip test because sqlite3 does not support upsert."""
        # Mocks
        mock_conn = mocker.MagicMock()
        mock_table = mocker.MagicMock()
        mock_table.table = "some_table"
        keys = ["id", "name"]
        data_iter = [(1, "Alice"), (2, "Bob")]

        mock_execute = mocker.MagicMock()
        mock_execute.rowcount = 2
        mock_conn.execute.return_value = mock_execute

        mock_insert = mocker.patch("sqlahandler.insert", autospec=True)
        mock_stmt = mocker.MagicMock()
        mock_stmt.on_duplicate_key_update.return_value = mock_stmt
        mock_insert.return_value = mock_stmt

        rowcount = SqlaHandler.upsert(mock_table, mock_conn, keys, data_iter)
        assert rowcount == 2
        mock_conn.execute.assert_called_once()

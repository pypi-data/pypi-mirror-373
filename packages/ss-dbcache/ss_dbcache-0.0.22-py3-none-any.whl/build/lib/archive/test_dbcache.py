"""
Created on 1 Jul 2025

@author: ph1jb
"""

from builtins import ValueError
from configargparse import Namespace  # type: ignore
from dbcache import CacheManager, Main  # adjust if named differently
from dotenv.main import dotenv_values
from models.cache import Cache
from pandas import DataFrame
from pathlib import Path
from sqlahandler import SqlaHandler
from sqlalchemy import delete
from sqlalchemy.sql import Select
from unittest.mock import ANY
import dbcache
import logging
import pandas as pd
import pymysql
import pytest
import sqlalchemy.exc
import yaml


# Mock Config
@pytest.fixture
def base_path():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def config_path(base_path):
    return base_path / "config" / "dbcache_config.yml"


@pytest.fixture
def env_var_paths(base_path):
    return [base_path / f".env.{suffix}_defaults" for suffix in ("common", "report")]


@pytest.fixture
def secrets_path(base_path):
    return base_path / "testdata" / "testdata_dbcache_secrets.yml"


@pytest.fixture
def config_d(config_path):
    with open(config_path, "r") as fin:
        return yaml.safe_load(fin)


@pytest.fixture
def env_var_d(env_var_paths):
    d = {}
    for f in env_var_paths:
        d.update(dotenv_values(f))
    del d["BASEDIR"]
    del d["RELEASE"]  # in .env but not a param
    return d


@pytest.fixture
def secrets_d(secrets_path):
    with open(secrets_path, "r") as fin:
        return yaml.safe_load(fin)


@pytest.fixture
def mock_engine():
    cnx_str = "mysql+pymysql://pvlive:***@ssfdb2.shef.ac.uk/pvdeployment"
    return sqlalchemy.create_engine(cnx_str)


@pytest.fixture
def sqlahandler_methods_mocked(mocker, mock_engine):
    for method in (
        "execute",
        "fetchall",
        "fetchone",
        "insert",
        "read_sql",
        "read_sql_query",
        "read_sql_table",
        "to_sql",
    ):
        mocker.patch.object(dbcache.SqlaHandler, method)
    return SqlaHandler(mock_engine)


##########################################################################################


@pytest.fixture
def cache_manager_mocked_qh(sqlahandler_methods_mocked):
    compression = "gzip"
    serialisation = "csv"
    return CacheManager(sqlahandler_methods_mocked, compression, serialisation)


class TestCacheManager:

    def test__deserialise_csv(self, cache_manager_mocked_qh):
        # Arrange
        data_raw = b"a,b\n0,1\n2,3"
        # Act
        result = cache_manager_mocked_qh._deserialise(data_raw)
        # Assert
        expected = DataFrame({"a": [0, 2], "b": [1, 3]})
        pd.testing.assert_frame_equal(result, expected)

    def test__deserialise_pickle(self, mocker, cache_manager_mocked_qh):
        # Arrange
        data_raw = b"a,b,c"
        df = DataFrame({"a": [0, 2], "b": [1, 3]})
        cache_manager_mocked_qh.serialisation = "pickle"
        mock_read_pickle = mocker.patch("dbcache.pd.read_pickle", return_value=df)
        # Act
        result = cache_manager_mocked_qh._deserialise(data_raw)
        # Assert
        mock_read_pickle.assert_called_once()
        expected = df
        pd.testing.assert_frame_equal(result, expected)

    def test__serialise_csv(self, cache_manager_mocked_qh):
        # Arrange
        df = DataFrame({"a": [0, 2], "b": [1, 3]})
        # Act
        result = cache_manager_mocked_qh._serialise(df, index=False)
        # Assert
        expected = b"a,b\n0,1\n2,3\n"
        assert result == expected

    def test__serialise_pickle(self, mocker, cache_manager_mocked_qh):
        # Arrange
        df = mocker.Mock()
        data_raw = "abc"
        mocker.patch.object(df, "to_pickle", return_value=data_raw)
        cache_manager_mocked_qh.serialisation = "pickle"
        # Act
        _result = cache_manager_mocked_qh._serialise(df)
        # Assert
        df.to_pickle.assert_called_once()

    def test__to_sql(self, mocker, cache_manager_mocked_qh):
        # Arrange
        data = b"abc"
        name = "name"
        table = "table"
        df = DataFrame({"name": name, "data": [data]})
        mocker.patch.object(
            cache_manager_mocked_qh.sqlahandler,
            "to_sql",
        )
        # Act
        cache_manager_mocked_qh._to_sql(table, data, name)
        # Assert
        cache_manager_mocked_qh.sqlahandler.to_sql.assert_called_once_with(
            ANY, table, if_exists="append", index=False, method=SqlaHandler.upsert
        )
        call_arg0 = cache_manager_mocked_qh.sqlahandler.to_sql.call_args[0][0]
        pd.testing.assert_frame_equal(call_arg0, df)

    def test_create_cache(self, cache_manager_mocked_qh):
        # Arrange
        statement = (
            f"CREATE TABLE IF NOT EXISTS cache ("
            "name varchar(100) NOT NULL,"
            "data longblob COMMENT 'Compressed data',"
            "PRIMARY KEY (name)"
            ") COMMENT='Cache table'"
        )
        # Act
        cache_manager_mocked_qh.create_cache()
        # Assert
        cache_manager_mocked_qh.sqlahandler.execute.assert_called_once_with(statement)

    def test_delete_cache(self, cache_manager_mocked_qh):
        # Arrange
        name = "name"

        # Act
        cache_manager_mocked_qh.delete_cache(name)

        # Assert
        # Cannot directly compare 2 sqlalchemy delete statements
        args, _ = cache_manager_mocked_qh.sqlahandler.execute.call_args
        statement = args[0]
        expected = delete(Cache).where(Cache.name == name)
        assert str(statement) == str(expected)
        assert statement.compile().params == expected.compile().params

    def test_read_cache_hit(self, mocker, cache_manager_mocked_qh):
        # Arrange
        cm = cache_manager_mocked_qh
        fake_data = b"compressed-bytes"
        deserialised_df = pd.DataFrame({"col": [1, 2, 3]})
        name = "test-cache"

        # Mock read_sql to return a DataFrame with a 'data' column
        read_sql_df = pd.DataFrame({"data": [fake_data]})
        mocker.patch.object(cm.sqlahandler, "read_sql", return_value=read_sql_df)

        # Mock the _deserialise method
        deserialise_mock = mocker.patch.object(cm, "_deserialise", return_value=deserialised_df)

        # Spy on logger
        mocker.patch("dbcache.logger")

        # --- Act ---
        result = cm.read_cache(name=name)

        # --- Assert ---
        cm.sqlahandler.read_sql.assert_called_once()
        deserialise_mock.assert_called_once_with(fake_data, compression={"method": "gzip"})
        pd.testing.assert_frame_equal(result, deserialised_df)

    def test_read_cache_miss(self, mocker, cache_manager_mocked_qh):
        # --- Setup ---
        name = "missing-cache"
        cm = cache_manager_mocked_qh
        cm.compression = "gzip"

        # mocker.Mock read_sql to return empty DataFrame
        mocker.patch.object(cm.sqlahandler, "read_sql", return_value=pd.DataFrame())

        # --- Act & Assert ---
        with pytest.raises(ValueError, match="Data not found"):
            cm.read_cache(cache_table="cache", name=name)

    def test_read_cache_logs_and_query_structure(self, mocker, cache_manager_mocked_qh):
        # --- Setup ---
        name = "log-test"
        fake_data = b"123"
        fake_df = pd.DataFrame({"data": [fake_data]})
        deserialised_df = pd.DataFrame({"x": [1]})

        cm = cache_manager_mocked_qh
        cm.compression = "zstd"

        # Patch read_sql and _deserialise
        read_sql_mock = mocker.patch.object(cm.sqlahandler, "read_sql", return_value=fake_df)
        mocker.patch.object(cm, "_deserialise", return_value=deserialised_df)

        # Spy on logger.debug
        log_spy = mocker.patch("dbcache.logger.debug")

        # --- Act ---
        result = cm.read_cache(cache_table="cache", name=name)

        # --- Assert ---
        read_sql_mock.assert_called_once()
        assert isinstance(read_sql_mock.call_args[0][0], Select)

        # Ensure logger.debug is called with expected messages
        debug_calls = [call[0][0] for call in log_spy.call_args_list]
        assert any("Selected compressed, serialised data." in msg for msg in debug_calls)
        assert any("Decompressed and deserialised data to DataFrame." in msg for msg in debug_calls)

    def test_read_data_from_cache(self, mocker, cache_manager_mocked_qh):
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_source"
        columns = "columns"
        df = DataFrame()
        #
        mocker.patch.object(cm, "read_cache", return_value=df)
        mocker.patch.object(cm, "update_cache", return_value=df)

        # Act
        result = cm.read_data(table_source, columns=columns)

        # Assert
        cm.read_cache.assert_called_once_with(table_source)
        pd.testing.assert_frame_equal(result, df)

    def test_read_data_from_table(self, mocker, cache_manager_mocked_qh):
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_source"
        columns = "columns"
        df = DataFrame()
        #
        mocker.patch.object(cm, "read_cache", side_effect=ValueError("Cache entry not found"))
        mocker.patch.object(cm, "update_cache", return_value=df)

        # Act
        result = cm.read_data(table_source, columns=columns)

        # Assert
        cm.update_cache.assert_called_once_with(table_source, columns=columns)
        pd.testing.assert_frame_equal(result, df)

    def test_read_table(self, mocker, cache_manager_mocked_qh):
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_source"
        kwargs = {
            "columns": ["id", "install_date"],
            "index_col": "id",
            "parse_dates": ["install_date"],
        }
        df = pd.DataFrame({"id": [1, 2], "install_date": ["2024-01-01", "2025-01-01"]})
        # Mocks
        mocker.patch.object(cm.sqlahandler, "read_sql", return_value=df)
        mocker.patch.object(cm, "write_cache")

        # Act
        result = cm.read_table(table_source, **kwargs)

        # Assert
        cm.sqlahandler.read_sql.assert_called_once_with(table_source, **kwargs)
        pd.testing.assert_frame_equal(result, df)

    def test_update_cache(self, mocker, cache_manager_mocked_qh):
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_source"
        columns = "columns"
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        mocker.patch.object(cm, "read_table", return_value=df)
        mocker.patch.object(cm, "write_cache")

        # Act
        result = cm.update_cache(table_source, columns=columns)

        # Assert
        cm.read_table.assert_called_once_with(table_source, columns=columns)
        cm.write_cache.assert_called_once_with(df, table_source)
        pd.testing.assert_frame_equal(result, df)

    def test_write_cache(self, mocker, cache_manager_mocked_qh):
        # Arrange
        cm = cache_manager_mocked_qh
        cm.compression = "gzip"
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        data = b"a,b\n1,3\n2,4\n"
        mocker.patch.object(cm, "_serialise", return_value=data)
        mocker.patch.object(cm, "_to_sql")

        # Act
        cm.write_cache(df, "name")

        # Assert
        cm._serialise.assert_called_once_with(df, compression={"method": "gzip"})
        cm._to_sql.assert_called_once_with("cache", data, "name")


class TestCacheManagerExceptions:
    """Test calls to read_data with various error conditions."""

    def test_key_not_found(self, mocker, cache_manager_mocked_qh):
        """Test read_data: key is not found in the cache then update the cache."""
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_source"
        columns = "columns"
        df = DataFrame()
        #
        mocker.patch.object(cm, "read_cache", side_effect=ValueError("Cache entry not found"))
        mocker.patch.object(cm, "update_cache", return_value=df)

        # Act
        result = cm.read_data(table_source, columns=columns)

        # Assert
        cm.update_cache.assert_called_once_with(table_source, columns=columns)
        assert result is df

    def test_cannot_read_cache_table(self, caplog, mocker, cache_manager_mocked_qh):
        """Test read_data: cannot read the cache table."""
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_source"
        columns = "columns"
        #
        mocker.patch.object(
            cm,
            "read_cache",
            side_effect=sqlalchemy.exc.ProgrammingError(
                "Table 'test_pvdeployment_julian.table_cacheXXX' doesn't exist",
                None,
                pymysql.err.ProgrammingError,
            ),
        )
        mocker.patch.object(cm, "update_cache")

        # Act
        cm.read_data(table_source, columns=columns)

        # Assert
        cm.update_cache.assert_called_once_with(table_source, columns=columns)

    def test_cannot_read_source_table(self, caplog, mocker, cache_manager_mocked_qh):
        """Test read_data: cannot read the source table."""
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_sourceXXX"
        columns = "columns"
        #
        mocker.patch.object(cm, "read_cache", side_effect=ValueError("Cache entry not found"))
        mocker.patch.object(
            cm,
            "read_table",
            side_effect=sqlalchemy.exc.ProgrammingError(
                "Table 'test_pvdeployment_julian.table_sourceXXX' doesn't exist",
                None,
                pymysql.err.ProgrammingError,
            ),
        )

        # Act
        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            cm.read_data(table_source, columns=columns)

        # Assert
        assert f"Key table_sourceXXX not found in cache table: cache" in caplog.text

    def test_cannot_write_cache_table(self, caplog, mocker, cache_manager_mocked_qh):
        """Test read_data: cannot write the cache table."""
        # Arrange
        cm = cache_manager_mocked_qh
        table_source = "table_sourceXXX"
        columns = "columns"
        df = DataFrame({"col0": [123]})
        #
        mocker.patch.object(cm, "read_cache", side_effect=ValueError("Cache entry not found"))
        mocker.patch.object(cm, "read_table", return_value=df)
        mocker.patch.object(
            cm,
            "write_cache",
            side_effect=sqlalchemy.exc.ProgrammingError(
                "Table 'test_pvdeployment_julian.table_sourceXXX' doesn't exist",
                None,
                pymysql.err.ProgrammingError,
            ),
        )

        # Act
        cm.read_data(table_source, columns=columns)

        # Assert
        cm.write_cache.assert_called_once_with(ANY, table_source)
        assert f"Key table_sourceXXX not found in cache table: cache" in caplog.text
        assert f"Cannot write to cache table: cache." in caplog.text


class TestMain:
    @pytest.fixture
    def mock_config(self):
        return Namespace(
            columns="id,name",
            compression="gzip",
            connector="mysqlclient",
            create_cache=False,
            delete_cache=False,
            index_col=None,
            loglevel="DEBUG",
            logformat="%(message)s",
            mysql_database="test_db",
            mysql_host="localhost",
            mysql_user="root",
            mysql_password="password",
            mysql_options={"host": "localhost", "database": "test_db"},
            parse_dates=None,
            serialisation="pickle",
            table_source="source_table",
            update_cache=False,
        )

    def test__create_sqlahandler(self, mocker, mock_engine):
        # Arrange: create a dummy config
        mysql_options = {
            "database": "test_db",
            "host": "localhost",
            "password": "password",
            "port": 3306,
            "user": "username",
        }
        config = Namespace(connector="mysqlclient", mysql_options=mysql_options)

        # Patch dependencies
        mock_create_engine = mocker.patch.object(
            dbcache.sqlalchemy, "create_engine", return_value=mock_engine
        )
        sqlahandler_methods_mocked = mocker.patch.object(dbcache, "SqlaHandler")
        url = "mysql+mysqlconnector://username:password@localhost:3306/test_db"
        mocker.patch.object(sqlahandler_methods_mocked, "sqlalchemy_url", return_value=url)

        # Act
        result = Main._create_sqlahandler(config)

        # Assert
        mock_create_engine.assert_called_once_with(url)
        sqlahandler_methods_mocked.assert_called_once_with(mock_engine)
        assert result == sqlahandler_methods_mocked.return_value

    def test_parse_config(self, mocker, mock_config):
        mock_parser = mocker.Mock()
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse_args.return_value = mock_config
        mocker.patch("dbcache.configargparse.ArgParser", mock_parser)

        config = Main._parse_config(Path("config.yml"), Path("secrets.yml"))
        assert config.table_source == "source_table"
        assert config.compression == "gzip"

    def test_setup_logging(self, mocker, mock_config):
        mock_basic_config = mocker.patch("dbcache.logging.basicConfig")
        Main._setup_logging(mock_config)
        mock_basic_config.assert_called_once_with(
            format=mock_config.logformat, level=mock_config.loglevel
        )

    def test_main_initialisation(
        self, mocker, mock_config, sqlahandler_methods_mocked, cache_manager_mocked_qh
    ):
        _mock_parse = mocker.patch.object(Main, "_parse_config", return_value=mock_config)

        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler", return_value=sqlahandler_methods_mocked)
        mocker.patch("dbcache.CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("config.yml"), Path("secrets.yml"))

        assert main.config == mock_config
        assert main.sqlahandler == sqlahandler_methods_mocked
        assert main.cache_manager == cache_manager_mocked_qh

    def test_run_create_cache(self, mocker, mock_config, cache_manager_mocked_qh):
        mock_config.create_cache = True
        mocker.patch.object(Main, "_parse_config", return_value=mock_config)
        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler")
        mocker.patch.object(cache_manager_mocked_qh, "create_cache")
        mocker.patch.object(dbcache, "CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("c"), Path("s"))
        main.run()

        cache_manager_mocked_qh.create_cache.assert_called_once_with()

    def test_run_delete_cache(self, mocker, mock_config, cache_manager_mocked_qh):
        mock_config.delete_cache = True
        mocker.patch.object(Main, "_parse_config", return_value=mock_config)
        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler")
        mocker.patch.object(cache_manager_mocked_qh, "delete_cache")

        mocker.patch.object(dbcache, "CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("c"), Path("s"))
        main.run()

        cache_manager_mocked_qh.delete_cache.assert_called_once_with("source_table")

    def test_run_update_cache(self, mocker, mock_config, cache_manager_mocked_qh):
        mock_config.update_cache = True
        mocker.patch.object(Main, "_parse_config", return_value=mock_config)
        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler")
        mocker.patch.object(cache_manager_mocked_qh, "update_cache")

        mocker.patch.object(dbcache, "CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("c"), Path("s"))
        main.run()

        cache_manager_mocked_qh.update_cache.assert_called_once_with(
            "source_table", columns="id,name", index_col=None, parse_dates=None
        )

    def test_run_read_data(self, mocker, mock_config, cache_manager_mocked_qh):
        # all three flags are False
        mocker.patch.object(Main, "_parse_config", return_value=mock_config)
        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler")
        mocker.patch.object(cache_manager_mocked_qh, "read_data")

        mocker.patch.object(dbcache, "CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("c"), Path("s"))
        main.run()

        cache_manager_mocked_qh.read_data.assert_called_once_with(
            "source_table", columns="id,name", index_col=None, parse_dates=None
        )

    def test_run_read_data_exception_DEBUG(
        self, caplog, mocker, mock_config, cache_manager_mocked_qh
    ):
        # all three flags are False
        mocker.patch.object(Main, "_parse_config", return_value=mock_config)
        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler")
        mocker.patch.object(Main, "_read_data_command", side_effect=ValueError())

        mocker.patch("dbcache.CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("c"), Path("s"))
        # Act & Assert
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(ValueError):
                main.run()

    def test_run_read_data_exception_INFO(
        self, caplog, mocker, mock_config, cache_manager_mocked_qh
    ):
        # all three flags are False
        mocker.patch.object(Main, "_parse_config", return_value=mock_config)
        mocker.patch.object(Main, "_setup_logging")
        mocker.patch.object(Main, "_create_sqlahandler")
        mocker.patch.object(Main, "_read_data_command", side_effect=ValueError("Error message"))

        mocker.patch("dbcache.CacheManager", return_value=cache_manager_mocked_qh)

        main = Main(Path("c"), Path("s"))
        # Act
        with caplog.at_level(logging.INFO):
            main.run()
        # Assert
        assert "Error message" in caplog.text

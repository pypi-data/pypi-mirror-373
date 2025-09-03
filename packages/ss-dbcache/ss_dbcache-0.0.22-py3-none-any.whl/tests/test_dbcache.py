"""
Created on 1 Jul 2025

@author: ph1jb
"""

from dbcache import CacheManager, Config, Main, Config
from io import BytesIO
from mypyc.irbuild import statement
from pathlib import Path
from pytest_mock import mocker
from sqlahandler import SqlaHandler
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock
import gzip
import logging
import logging
import pandas as pd
import pickle
import pytest
import sqlalchemy


@pytest.fixture
def dummy_df():
    return pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})


@pytest.fixture
def mock_sqlahandler(mocker):
    return mocker.MagicMock()


@pytest.fixture
def cache_manager(request, mock_sqlahandler):
    compression = request.param["compression"]
    serialisation = request.param["serialisation"]
    return CacheManager(mock_sqlahandler, compression=compression, serialisation=serialisation)


@pytest.fixture
def dummy_config(mocker):
    config = SimpleNamespace(
        create_cache=False,
        delete_cache=False,
        update_cache=False,
        table_source="test_table",
        compression="gzip",
        serialisation="pickle",
        columns=["col1", "col2"],
        index_col="col1",
        parse_dates=["install_date"],
        loglevel="INFO",
        logformat=Config.logformat_default,
        connector="pymysql",
        mysql_options={
            "user": "root",
            "password": "root",
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
        },
        mysql_database="dummy_database",
        mysql_host="dummy_host",
        mysql_password="dummy_password",
        mysql_user="dummy_user",
    )
    cache_manager = mocker.Mock()
    return SimpleNamespace(config=config, cache_manager=cache_manager)


@pytest.mark.parametrize(
    "cache_manager",
    [
        {"compression": "bz2", "serialisation": "csv"},
        {"compression": "bz2", "serialisation": "pickle"},
        {"compression": "gzip", "serialisation": "csv"},
        {"compression": "gzip", "serialisation": "pickle"},
    ],
    indirect=True,
)
class TestCacheManager:
    """Test core methods with compression = bz2 or gzip and serialisation = csv or pickle."""

    def test_serialise_deserialise(self, cache_manager, dummy_df):
        """Test serialise/deserialise round trip.
        Omit index when serialising to csv"""
        kwargs = {"index": False} if cache_manager.serialisation == "csv" else {}
        data = cache_manager._serialise(dummy_df, **kwargs)
        assert isinstance(data, bytes)
        df_restored = cache_manager._deserialise(data)
        pd.testing.assert_frame_equal(df_restored, dummy_df)

    def test_write_to_cache_table_calls_sqlahandler_to_sql_table(
        self, cache_manager, mock_sqlahandler
    ):
        # Act
        cache_manager._write_to_cache_table("cache", b"fake-bytes", "test_key")
        # Assert
        mock_sqlahandler.to_sql.assert_called_once_with(
            ANY, "cache", if_exists="append", index=False, method=SqlaHandler.upsert
        )

    def test_create_cache_executes_create_statement(self, mocker, cache_manager, mock_sqlahandler):
        # Arrange
        mock_create_all = mocker.patch("dbcache.Base.metadata.create_all")
        # Act
        cache_manager.create_cache()
        # Assert
        mock_create_all.assert_called_once()

    def test_delete_cache_uses_sqlalchemy_delete(self, cache_manager, mock_sqlahandler, mocker):
        mock_delete = mocker.patch("dbcache.delete")
        cache_manager.delete_cache("mykey")
        assert mock_sqlahandler.execute.called
        assert mock_delete.called

    def test_write_cache_calls_serialise_and_write_to_cache_table(
        self, cache_manager, mocker, dummy_df
    ):
        serialise_spy = mocker.spy(cache_manager, "_serialise")
        to_sql_spy = mocker.spy(cache_manager, "_write_to_cache_table")
        cache_manager.write_cache(dummy_df, "test_key")

        assert serialise_spy.called
        assert to_sql_spy.called

    def test_read_cache_returns_dataframe(self, cache_manager, mock_sqlahandler, dummy_df, mocker):
        # Arrange
        kwargs = {"index": False} if cache_manager.serialisation == "csv" else {}
        compression = cache_manager.compression
        data_bytes = cache_manager._serialise(dummy_df, **kwargs)

        mock_sqlahandler.read_sql_query.return_value = pd.DataFrame({"data": [data_bytes]})

        # Act
        df = cache_manager.read_cache("test_key")
        # Assert
        pd.testing.assert_frame_equal(df, dummy_df)

    def test_read_cache_empty_raises_ValueError(self, cache_manager, mock_sqlahandler):
        mock_sqlahandler.read_sql.return_value = pd.DataFrame(columns=["data"])
        with pytest.raises(ValueError, match="Data not found"):
            cache_manager.read_cache("missing_key")

    @pytest.mark.parametrize(
        "exception,args",
        [
            (sqlalchemy.exc.ProgrammingError, ("h", {}, "hi")),
            (sqlalchemy.exc.SQLAlchemyError, ("h", {}, "hi")),
            (IOError, ("h", {}, "hi")),
        ],
    )
    def test_read_data_raises_Error(self, cache_manager, mock_sqlahandler, exception, args):
        mock_sqlahandler.read_sql_table.side_effect = exception(*args)
        with pytest.raises(exception):
            cache_manager.read_data("missing_key")

    def test_read_data_returns_from_cache(self, cache_manager, mocker, dummy_df):
        mock_read_cache = mocker.patch.object(cache_manager, "read_cache", return_value=dummy_df)
        df = cache_manager.read_data("test_table")
        mock_read_cache.assert_called_once()
        pd.testing.assert_frame_equal(df, dummy_df)

    def test_read_data_falls_back_to_update_cache_on_cache_miss(
        self, cache_manager, mocker, dummy_df
    ):
        mocker.patch.object(cache_manager, "read_cache", side_effect=ValueError("Data not found"))
        mock_update_cache = mocker.patch.object(
            cache_manager, "update_cache", return_value=dummy_df
        )

        df = cache_manager.read_data("test_table")
        mock_update_cache.assert_called_once_with("test_table")
        pd.testing.assert_frame_equal(df, dummy_df)

    def test_update_cache_calls_write_cache(self, cache_manager, mocker, dummy_df):
        mock_read_table = mocker.patch.object(cache_manager, "read_table", return_value=dummy_df)
        mock_write_cache = mocker.patch.object(cache_manager, "write_cache")

        df = cache_manager.update_cache("table_source")
        mock_read_table.assert_called_once()
        mock_write_cache.assert_called_once()
        pd.testing.assert_frame_equal(df, dummy_df)

    def test_read_table_uses_sqlahandler_read_sql(self, cache_manager, mock_sqlahandler):
        df_mock = pd.DataFrame({"col": [1]})
        mock_sqlahandler.read_sql_table.return_value = df_mock
        result = cache_manager.read_table("source_table")
        pd.testing.assert_frame_equal(result, df_mock)
        mock_sqlahandler.read_sql_table.assert_called_once_with("source_table")


class TestCacheManagerExceptions:
    @pytest.fixture
    def cache_manager(self, mock_sqlahandler):
        return CacheManager(mock_sqlahandler, compression="gzip", serialisation="pickle")

    def test__deserialise_BadGzipFile(self, cache_manager):
        """pd.read_pickle with compression, raises a TypeError if the decompression fails."""
        # Bad data byte string: does not decompress and deserialise to a DataFrame
        data_raw = b"hi"
        with pytest.raises(gzip.BadGzipFile):
            cache_manager._deserialise(data_raw)

    def test__deserialise_BadPickle(self, cache_manager):
        """Deserialise to a string (not a DataFrame). Raises a TypeError."""
        # Bad data byte string: does not decompress and deserialise to a DataFrame
        data_raw = b"hi"
        cache_manager.compression = None
        with pytest.raises(pickle.UnpicklingError):
            cache_manager._deserialise(data_raw)

    def test__deserialise_BadDataFrame(self, cache_manager):
        """Deserialise to a string (not a DataFrame). Raises a TypeError."""
        # Bad data byte string: does not decompress and deserialise to a DataFrame
        data_raw = pickle.dumps("hi")
        cache_manager.compression = None
        with pytest.raises(ValueError, match="Not a DataFrame"):
            cache_manager._deserialise(data_raw)

    def test_read_cache_raises_value_error_on_cache_miss(self, cache_manager, mock_sqlahandler):
        # Simulate no matching rows in cache
        mock_sqlahandler.read_sql.return_value = pd.DataFrame(columns=["data"])
        with pytest.raises(ValueError, match="Data not found"):
            cache_manager.read_cache("missing_key")

    def test_read_cache_logs_and_raises_on_programming_error(
        self, cache_manager, mock_sqlahandler, mocker
    ):
        # Simulate SQL error when reading
        error = sqlalchemy.exc.ProgrammingError("stmt", {}, None)
        mock_sqlahandler.read_sql_query.side_effect = error

        # Mock logger
        mock_logger = mocker.patch("dbcache.logger")

        # Let the exception propagate
        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            cache_manager.read_cache("any_key")

        mock_logger.debug.assert_called()

    def test_read_data_warns_and_calls_update_cache_on_value_error(
        self, cache_manager, mocker, dummy_df
    ):
        # Simulate cache miss
        mocker.patch.object(cache_manager, "read_cache", side_effect=ValueError("Data not found"))
        mock_update = mocker.patch.object(cache_manager, "update_cache", return_value=dummy_df)
        mock_logger = mocker.patch("dbcache.logger")

        result = cache_manager.read_data("source_table")

        mock_logger.warning.assert_called()
        mock_update.assert_called_once()
        pd.testing.assert_frame_equal(result, dummy_df)

    def test_read_data_warns_on_programming_error_in_cache_read(
        self, cache_manager, mocker, dummy_df
    ):
        # Simulate SQL error reading from cache
        mocker.patch.object(
            cache_manager,
            "read_cache",
            side_effect=sqlalchemy.exc.ProgrammingError("stmt", {}, None),
        )
        mock_update = mocker.patch.object(cache_manager, "update_cache", return_value=dummy_df)
        mock_logger = mocker.patch("dbcache.logger")

        result = cache_manager.read_data("source_table")

        mock_logger.warning.assert_called()
        mock_update.assert_called_once()
        pd.testing.assert_frame_equal(result, dummy_df)

    def test_update_cache_warns_on_write_failure(self, cache_manager, mocker, dummy_df):
        # Mock data read to succeed
        mocker.patch.object(cache_manager, "read_table", return_value=dummy_df)
        # Simulate failure on cache write
        mocker.patch.object(
            cache_manager,
            "write_cache",
            side_effect=sqlalchemy.exc.ProgrammingError("stmt", {}, None),
        )
        mock_logger = mocker.patch("dbcache.logger")

        # Should return the df even if write fails
        df = cache_manager.update_cache("source_table")
        mock_logger.warning.assert_any_call(
            "Cannot write to cache table: cache. %(_err)s", {"_err": mocker.ANY}
        )
        pd.testing.assert_frame_equal(df, dummy_df)


class TestConfig:
    def test__init__(self, mocker, tmp_path):
        mock_parse_config = mocker.patch("dbcache.Config._parse_config")
        mock_setup_logging = mocker.patch("dbcache.Config._setup_logging")
        # Act
        config = Config(tmp_path, tmp_path)
        # Assert
        mock_parse_config.assert_called_once_with(tmp_path, tmp_path)

    # Path("config.yml"), Path("secrets.yml")
    # mocker.patch("dbcache.Main._parse_config", return_value=dummy_config)
    def test_parse_config_loads_config_file(self, mocker, tmp_path):
        # Simulate YAML config file behavior
        config_path = tmp_path / "config.yml"
        secrets_path = tmp_path / "secrets.yml"
        config_path.write_text("dummy: yes")
        secrets_path.write_text("dummy: yes")

        mock_parser = mocker.MagicMock()
        mock_parser.return_value.parse_args.return_value = SimpleNamespace(dummy="value")

        mock_argparser_cls = mocker.patch(
            "dbcache.configargparse.ArgParser", return_value=mock_parser
        )

        result = Config._parse_config(config_path, secrets_path)
        assert hasattr(result, "dummy")
        mock_argparser_cls.assert_called_once()
        # mock_parser.return_value.parse_args.assert_called_once()

    def test_setup_logging_configures_basic_config(self, mocker):
        mock_basic_config = mocker.patch("dbcache.logging.basicConfig")

        Config._setup_logging(format="FORMAT", level="DEBUG")
        mock_basic_config.assert_called_once_with(format="FORMAT", level="DEBUG")


class TestMain:

    @pytest.fixture
    def main_instance(self, dummy_config, mocker):
        mock_cache_manager = mocker.MagicMock()
        mock_create_cache_manager = mocker.patch("dbcache.Main._create_cache_manager")
        mock_create_sqlahandler = mocker.patch("dbcache.Main._create_sqlahandler")
        return Main(dummy_config)

    def test_create_cache_manager_returns_instance(self, mocker):
        mock_sqlahandler = mocker.MagicMock(spec=SqlaHandler)
        cm = Main._create_cache_manager(mock_sqlahandler, "gzip", "csv")
        assert isinstance(cm, CacheManager)
        assert cm.compression == "gzip"
        assert cm.serialisation == "csv"

    def test_create_sqlahandler_returns_instance(self, mocker):
        # Mock config with minimal mysql options
        config = SimpleNamespace(
            connector="pymysql",
            mysql_options={
                "user": "user",
                "password": "pass",
                "host": "localhost",
                "port": 3306,
                "database": "testdb",
            },
            mysql_database=None,
            mysql_host=None,
            mysql_user=None,
            mysql_password=None,
        )
        mock_engine = mocker.MagicMock()
        mock_url = mocker.patch("dbcache.sqlalchemy.create_engine", return_value=mock_engine)

        handler = Main._create_sqlahandler(config)
        assert isinstance(handler, SqlaHandler)
        mock_url.assert_called_once()

    def test_create_cache_command_calls_cache_manager(self, main_instance):
        main_instance._create_cache_command()
        main_instance.cache_manager.create_cache.assert_called_once()

    def test_delete_cache_command_calls_cache_manager(self, main_instance):
        main_instance._delete_cache_command()
        main_instance.cache_manager.delete_cache.assert_called_once_with("test_table")

    def test_update_cache_command_calls_cache_manager_with_expected_args(self, main_instance):
        main_instance._update_cache_command()
        main_instance.cache_manager.update_cache.assert_called_once_with(
            "test_table",
            columns=["col1", "col2"],
            index_col="col1",
            parse_dates=["install_date"],
        )

    def test_read_data_command_calls_cache_manager_with_expected_args(self, main_instance):
        df_mock = pytest.importorskip("pandas").DataFrame({"a": [1]})
        main_instance.cache_manager.read_data.return_value = df_mock

        main_instance._read_data_command()

        main_instance.cache_manager.read_data.assert_called_once_with(
            "test_table",
            columns=["col1", "col2"],
            index_col="col1",
            parse_dates=["install_date"],
        )


class TestMainExceptions:

    def test_main_run_logs_exception_if_not_debug(self, mocker, dummy_config):
        # Mock Main methods and config
        mock_logger = mocker.patch("dbcache.logger")
        mock_logger.getEffectiveLevel.return_value = logging.INFO

        main = Main(dummy_config)
        # Simulate exception in default read_data command
        main.command_map["read_data"] = mocker.Mock(side_effect=RuntimeError("Boom"))

        main.run()

        mock_logger.error.assert_called_with(("Boom",))

    def test_main_run_reraises_exception_if_debug(self, mocker, dummy_config):
        mock_logger = mocker.patch("dbcache.logger")
        mock_logger.getEffectiveLevel.return_value = logging.DEBUG

        main = Main(dummy_config)
        main.command_map["read_data"] = mocker.Mock(side_effect=RuntimeError("Boom"))

        with pytest.raises(RuntimeError, match="Boom"):
            main.run()

    @pytest.mark.parametrize(
        "option",
        ["create_cache", "delete_cache", "update_cache", "read_data"],
    )
    def test_main_run_executes_first_command_flag(self, mocker, dummy_config, option):
        setattr(dummy_config.config, option, True)  # Trigger only this command

        mock_create = mocker.Mock()
        mock_delete = mocker.Mock()
        mock_read_data = mocker.Mock()
        mock_update = mocker.Mock()

        main = Main(dummy_config)

        main.command_map = {
            "create_cache": mock_create,
            "delete_cache": mock_delete,
            "update_cache": mock_update,
            "read_data": mock_read_data,
        }
        # Act
        main.run()

        # Assert

        # Assert the expected one was called, the others were not
        for key, mock in main.command_map.items():
            if key == option:
                mock.assert_called_once()
            else:
                mock.assert_not_called()

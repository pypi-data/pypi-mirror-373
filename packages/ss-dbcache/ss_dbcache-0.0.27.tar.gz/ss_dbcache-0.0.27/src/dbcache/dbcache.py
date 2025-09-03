#!/bin/env python3
"""
Created on 9 Mar 2025

@author: ph1jb.
Cache large table as a long blob.

Serialise DataFrame, compress, insert; select, decompress, deserialise to DataFrame.
Uses sqlalchemy
Connectors
* mysqlconnector: on large tables (e.g. sitelist, ~180Mb) fails with csv, OK with pickle
* mysqlclient: OK
* pymysql: OK
Compression libs usable with pandas serialisation: bz2, gzip, xz, zstd.
* gzip: 
  + Compressed data size: 48489691
  + decompress & deserialise: ~ 1s
* xz: Compressed data size: 23284368
  + Compressed data size: 48489691
  + decompress & deserialise: ~ 7s
Timings
select & fetch: 12s
https://www.rootusers.com/gzip-vs-bzip2-vs-xz-performance-comparison/
mysqlclient needs:  export LD_PRELOAD=/lib/x86_64-linux-gnu/libstdc++.so.6:$LD_PRELOAD
We hard code the cache table name as cache for security because we write to the cache.

Error handling:
  cache miss: key not found in cache table: raise and catch ValueError. Update cache
  cannot read from cache table: permission denied or database.table not found
  cannot read from source table: permission denied or database.table not found
  cannot write to cache table: permission denied or database.table not found
"""

from configargparse import Namespace, YAMLConfigFileParser  # type: ignore
from io import BytesIO
from models.base import Base
from models.cache import Cache  # type: ignore
from pandas import DataFrame
from pathlib import Path
from sqlahandler import SqlaHandler  # type: ignore
from sqlalchemy import delete, select
from typing import Literal, Dict, Callable
import configargparse
import datetime
import dotenv
import logging
import pandas as pd
import sqlalchemy
import yaml


logger = logging.getLogger(__name__)
type Compression = Literal["bz2", "gzip", "xz", "zlib"]
type Connector = Literal["mysqlconnector", "mysqlclient", "pymysql"]
type Serialisation = Literal["csv", "pickle"]


class CacheManager:
    """
    Manage cache operations: serialize DataFrame, compress, insert;
    select, decompress, deserialize to DataFrame.

    :param sqlahandler: SQLAlchemy handler for database operations
    :type sqlahandler: SqlaHandler
    :param compression: Compression method
    :type compression: Compression
    :param serialisation: Serialization format
    :type serialisation: Serialisation
    """

    def __init__(
        self,
        sqlahandler: SqlaHandler,
        compression: Compression = "gzip",
        serialisation: Serialisation = "pickle",
    ) -> None:
        self.sqlahandler = sqlahandler
        self.compression = compression
        self.serialisation = serialisation

    def _deserialise(self, data_raw: bytes, **kwargs) -> DataFrame:
        """
        Deserialize raw bytes into a DataFrame.

        :param data_raw: Raw compressed and serialized data
        :type data_raw: bytes
        :param kwargs: Additional keyword arguments for pandas
        :return: Deserialized DataFrame
        :rtype: DataFrame
        :raises ValueError: If result is not a DataFrame
        """
        kwargs.update({"compression": {"method": self.compression}})
        if self.serialisation == "csv":
            df = pd.read_csv(BytesIO(data_raw), **kwargs)
        elif self.serialisation == "pickle":
            df = pd.read_pickle(BytesIO(data_raw), **kwargs)
        if not isinstance(df, DataFrame):
            raise ValueError("Not a DataFrame")
        return df

    def _serialise(self, df: DataFrame, **kwargs) -> bytes:
        """
        Serialize a DataFrame into compressed bytes.

        :param df: DataFrame to serialize
        :type df: DataFrame
        :param kwargs: Additional keyword arguments for pandas
        :return: Compressed serialized data
        :rtype: bytes
        """
        kwargs.update({"compression": {"method": self.compression}})
        raw_buffer = BytesIO()
        if self.serialisation == "csv":
            df.to_csv(raw_buffer, **kwargs)
        elif self.serialisation == "pickle":
            df.to_pickle(raw_buffer, **kwargs)
        return raw_buffer.getvalue()

    def _write_to_cache_table(self, table: str, data: bytes, name: str) -> None:
        """
        Insert serialized, compressed data into cache table.

        :param table: Table name
        :type table: str
        :param data: Compressed serialized data
        :type data: bytes
        :param name: Cache key
        :type name: str
        """
        df = DataFrame({"name": [name], "data": [data]})
        self.sqlahandler.to_sql(
            df, table, if_exists="append", index=False, method=SqlaHandler.upsert
        )

    def create_cache(self) -> None:
        """Create cache table if it does not exist."""
        logger.debug("Creating cache table.")
        Base.metadata.create_all(self.sqlahandler.engine)  # @UndefinedVariable
        logger.debug("Created cache table.")

    def delete_cache(self, name: str) -> None:
        """
        Delete a row from the cache table by name.

        :param name: Cache key
        :type name: str
        """
        statement = delete(Cache).where(Cache.name == name)
        self.sqlahandler.execute(statement)

    def read_cache(self, name: str, **kwargs) -> DataFrame:
        """
        Retrieve and deserialize data from the cache.

        :param name: Cache key
        :type name: str
        :param kwargs: Additional parameters for SQLAlchemy
        :return: Retrieved DataFrame
        :rtype: DataFrame
        :raises ValueError: If data not found
        """
        logger.debug("Selecting compressed, serialized data from cache table.")
        start_at = datetime.datetime.now()

        if not isinstance(name, str) or len(name) > 100:
            raise ValueError("Suspect name: {name}")

        statement = select(Cache.data).where(Cache.name == name).limit(1)
        df = self.sqlahandler.read_sql_query(statement, **kwargs)
        if df.empty:
            raise ValueError("Data not found")

        data = df.at[0, "data"]
        logger.debug("Selected data. Length: %(_len)s", {"_len": len(data)})

        df = self._deserialise(data)

        duration = (datetime.datetime.now() - start_at).total_seconds()
        logger.debug("Retrieved and deserialized in %(duration)s s", {"duration": duration})
        return df

    def read_data(self, table_source: str, **kwargs) -> DataFrame:
        """
        Get data from cache or fallback to source table, updating cache.

        :param table_source: Source table name
        :type table_source: str
        :param kwargs: Additional parameters
        :return: Resulting DataFrame
        :rtype: DataFrame
        """
        try:
            return self.read_cache(table_source)
        except ValueError:
            logger.warning("Key %(key)s not found in cache.", {"key": table_source})
        except sqlalchemy.exc.ProgrammingError as _err:
            logger.warning("Cannot read cache table: %(_err)s", {"_err": _err})
        except sqlalchemy.exc.SQLAlchemyError:
            logger.exception("Unexpected SQLAlchemy error")
            raise
        except (IOError, OSError) as _err:
            logger.exception("Error: %(_err)s", {"_err": _err})
            raise

        logger.warning("Updating cache for %(table_source)s", {"table_source": table_source})
        return self.update_cache(table_source, **kwargs)

    def read_table(self, table_source: str, **kwargs) -> DataFrame:
        """
        Select data from source table.

        :param table_source: Source table name
        :type table_source: str
        :param kwargs: Additional parameters (e.g., columns)
        :return: DataFrame from table
        :rtype: DataFrame
        """
        logger.debug("Selecting data from source table.")
        start_at = datetime.datetime.now()
        df = self.sqlahandler.read_sql_table(table_source, **kwargs)
        duration = (datetime.datetime.now() - start_at).total_seconds()
        logger.debug("Fetched data in %(duration)s s", {"duration": duration})
        return df

    def update_cache(self, table_source: str, **kwargs) -> DataFrame:
        """
        Update cache with data from source.

        :param table_source: Source table name
        :type table_source: str
        :param kwargs: Parameters like columns, index_col, parse_dates
        :return: DataFrame that was cached
        :rtype: DataFrame
        """
        logger.debug("Update cache: selecting data from source table...")
        df = self.read_table(table_source, **kwargs)
        logger.debug("Serializing, compressing, inserting into cache")
        try:
            self.write_cache(df, table_source)
        except sqlalchemy.exc.ProgrammingError as _err:
            logger.warning("Cannot write to cache table: %(_err)s", {"_err": _err})
        return df

    def write_cache(self, df: DataFrame, name: str) -> None:
        """
        Serialize and write DataFrame to cache.

        :param df: DataFrame to cache
        :type df: DataFrame
        :param name: Cache key
        :type name: str
        """
        logger.debug("Serializing and compressing DataFrame. Nrows: %(nrows)s", {"nrows": len(df)})
        data = self._serialise(df)
        logger.debug("Data length: %(len)s", {"len": len(data)})
        self._write_to_cache_table("cache", data, name)
        logger.debug("Inserted serialized, compressed data")


class Config:
    """
    Load and manage configuration from files, CLI, and environment.

    :param config_file: Path to configuration YAML file
    :type config_file: Path
    :param secrets_file: Path to secrets YAML file
    :type secrets_file: Path
    """

    logformat_default = "%(asctime)s %(module)s %(funcName)s %(lineno)d %(levelname)s %(message)s"
    columns_default = "id,source,source_id,longitude,latitude,install_date,dc_capacity_mwp"

    def __init__(self, config_file: Path, secrets_file: Path) -> None:
        self.config: Namespace = self._parse_config(config_file, secrets_file)
        self._setup_logging(format=self.config.logformat, level=self.config.loglevel)
        logger.debug("Compression: %(lib)s", {"lib": self.config.compression})
        logger.debug("Serialisation: %(sf)s", {"sf": self.config.serialisation})

    @staticmethod
    def _parse_config(config_file: Path, secrets_file: Path) -> Namespace:
        """
        Parse arguments from CLI, config files, and environment variables.

        :param config_file: Path to main config YAML file
        :type config_file: Path
        :param secrets_file: Path to secrets YAML file
        :type secrets_file: Path
        :return: Namespace containing configuration
        :rtype: Namespace
        """
        p = configargparse.ArgParser(
            config_file_parser_class=YAMLConfigFileParser,
            default_config_files=[config_file, secrets_file],
        )
        p.add(
            "--columns",
            action="append",
            default=[],
            env_var="COLUMNS",
            help="List of columns to select from source table",
        )
        p.add(
            "--compression",
            choices=["bz2", "gzip", "xz", "zlib"],
            default="gzip",
            env_var="COMPRESSION",
            help="Compression lib",
        )
        p.add(
            "--connector",
            choices=["mysqlconnector", "mysqlclient", "pymysql"],
            default="pymysql",
            env_var="CONNECTOR",
            help="MySQL connector",
        )
        p.add(
            "--create_cache",
            action="store_true",
            env_var="CREATE_CACHE",
            help="Create cache table (if not exists).",
        )
        p.add(
            "--delete_cache",
            action="store_true",
            env_var="DELETE_CACHE",
            help="Delete row from cache table.",
        )
        p.add("--index_col", default=None, env_var="INDEX_COL", help="Column to set as index.")
        p.add_argument(
            "--loglevel",
            choices=["INFO", "WARNING", "DEBUG", "ERROR", "CRITICAL"],
            default="INFO",
            env_var="LOGLEVEL",
            help="Log level",
        )
        p.add_argument(
            "--logformat", default=Config.logformat_default, env_var="LOGFORMAT", help="Log format"
        )
        p.add("--mysql_database", env_var="MYSQL_DATABASE", help="Database name")
        p.add("--mysql_host", env_var="MYSQL_HOST", help="Database host")
        p.add("--mysql_user", env_var="MYSQL_USER", help="Database user")
        p.add("--mysql_password", help="Database password.")
        p.add(
            "--mysql_options",
            env_var="MYSQL_OPTIONS",
            required=True,
            type=yaml.safe_load,
            help="MySQL options",
        )
        p.add(
            "--parse_dates",
            action="append",
            default=None,
            env_var="PARSE_DATES",
            help="Columns to parse as dates.",
        )
        p.add(
            "--serialisation",
            choices=["csv", "pickle"],
            default="pickle",
            env_var="SERIALISATION",
            help="Serialisation format",
        )
        p.add("--table_source", env_var="TABLE_SOURCE", required=True, help="Source table")
        p.add("--update_cache", action="store_true", env_var="UPDATE_CACHE", help="Update cache")
        logger.debug("Parsing configuration arguments.")
        return p.parse_args()

    @staticmethod
    def _setup_logging(**kwargs) -> None:
        """
        Set up logging based on configuration.

        :param kwargs: Logging configuration arguments
        :type kwargs: dict
        """
        logging.basicConfig(**kwargs)


class Main:
    """
    Main class to execute cache commands based on configuration.

    :param config: Config instance with parsed parameters
    :type config: Config
    """

    def __init__(self, config: Config) -> None:
        self.config = config.config
        logger.debug(config)
        sqlahandler = Main._create_sqlahandler(self.config)
        self.cache_manager = Main._create_cache_manager(
            sqlahandler, self.config.compression, self.config.serialisation
        )
        self.command_map: Dict[str, Callable[[], None]] = {
            "create_cache": self._create_cache_command,
            "delete_cache": self._delete_cache_command,
            "update_cache": self._update_cache_command,
            "read_data": self._read_data_command,
        }

    @staticmethod
    def _create_cache_manager(
        sqlahandler: SqlaHandler,
        compression: Compression = "gzip",
        serialisation: Serialisation = "pickle",
    ) -> CacheManager:
        """
        Instantiate CacheManager with provided options.

        :param sqlahandler: SQLAlchemy handler
        :type sqlahandler: SqlaHandler
        :param compression: Compression method
        :type compression: Compression
        :param serialisation: Serialization format
        :type serialisation: Serialisation
        :return: CacheManager instance
        :rtype: CacheManager
        """
        return CacheManager(sqlahandler, compression=compression, serialisation=serialisation)

    @staticmethod
    def _create_sqlahandler(config: Namespace) -> SqlaHandler:
        """
        Create and configure a SQLAlchemy handler.

        :param config: Configuration namespace
        :type config: Namespace
        :return: SQLAlchemy handler
        :rtype: SqlaHandler
        """
        mysql_overrides = SqlaHandler.get_mysql_overrides(config)
        sqla_options = SqlaHandler.get_sqla_options(config.mysql_options, mysql_overrides)
        drivername = "mysql" if (config.connector == "mysqlclient") else f"mysql+{config.connector}"
        sqla_url = SqlaHandler.get_sqla_url(sqla_options, drivername=drivername)
        engine = sqlalchemy.create_engine(sqla_url)
        logger.debug("Database connection string: %s", engine)
        return SqlaHandler(engine)

    def _create_cache_command(self) -> None:
        """Create cache table."""
        logger.debug("Creating cache table.")
        self.cache_manager.create_cache()
        logger.debug("Created cache table.")

    def _delete_cache_command(self) -> None:
        """Delete a row from the cache table."""
        logger.debug("Deleting data from cache.")
        self.cache_manager.delete_cache(self.config.table_source)
        logger.debug("Deleted data from cache.")

    def _update_cache_command(self) -> None:
        """Update the cache table with a single row of data."""
        logger.debug("Updating cache from source table.")
        self.cache_manager.update_cache(
            self.config.table_source,
            columns=self.config.columns,
            index_col=self.config.index_col,
            parse_dates=self.config.parse_dates,
        )
        logger.debug("Updated cache.")

    def _read_data_command(self) -> None:
        """Read data from the cache table."""
        df = self.cache_manager.read_data(
            self.config.table_source,
            columns=self.config.columns,
            index_col=self.config.index_col,
            parse_dates=self.config.parse_dates,
        )
        logger.debug(df)
        logger.debug(df.dtypes)

    def run(self) -> None:
        """
        Execute command as specified in the configuration.
        Stops after first matching command.
        """
        try:
            for cmd_flag, method in self.command_map.items():
                if getattr(self.config, cmd_flag, False):
                    method()
                    break
            else:
                self.command_map["read_data"]()
        except Exception as _ex:
            if logger.getEffectiveLevel() == logging.DEBUG:
                raise
            logger.error(_ex.args)


#
# class Config:
#     def __init__(self, config) -> None:
#         self.config = config
#         self._setup_logging(config)
#         sqlahandler = Config._create_sqlahandler(config)
#         self.cache_manager = Config._create_cache_manager(
#             sqlahandler, config.compression, config.serialisation
#         )
#         logger.debug("Compression: %(lib)s", {"lib": config.compression})
#         logger.debug("Serialisation: %(sf)s", {"sf": config.serialisation})
#
#     @staticmethod
#     def _create_cache_manager(
#         sqlahandler: SqlaHandler, compression: Compression, serialisation: Serialisation
#     ) -> CacheManager:
#         """Create an instance of CacheManager."""
#         return CacheManager(sqlahandler, compression, serialisation)
#
#     @staticmethod
#     def _create_sqlahandler(config: Namespace) -> SqlaHandler:
#         """Create an instance of SqlaHandler."""
#         SqlaHandler.override_mysql_options(config)
#         drivername = "mysql" if (config.connector == "mysqlclient") else f"mysql+{config.connector}"
#         cnx_str = SqlaHandler.sqlalchemy_url(config.mysql_options, drivername=drivername)
#         engine = sqlalchemy.create_engine(cnx_str)
#         logger.debug("Database connection string: %s", engine)
#         return SqlaHandler(engine)
#
#     @staticmethod
#     def _setup_logging(config) -> None:
#         """Set up logging."""
#         logging.basicConfig(format=config.logformat, level=config.loglevel)


# Main Execution
if __name__ == "__main__":
    dotenv.load_dotenv(override=True)
    CONFIG_FILE = Path(__file__).resolve().parent.parent / "config" / "dbcache_config.yml"
    SECRETS_FILE = Path(__file__).resolve().parent.parent / "secrets" / "dbcache_secrets.yml"
    CONFIG = Config(CONFIG_FILE, SECRETS_FILE)
    MAIN = Main(CONFIG)
    MAIN.run()
    logger.debug("Done.")

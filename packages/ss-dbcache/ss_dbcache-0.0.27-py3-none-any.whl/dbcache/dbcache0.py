#!/bin/env python3
"""
Created on 9 Mar 2025

@author: ph1jb.
Cache large table as a long blob.

Serialise DataFrame, compress, insert; select, decompress, deserialise to DataFrame.
Using sqlalchemy
sqlalchemy Fails with with mysqlconnector.
Works with sqlalchemy with mysqlclient, pymysql.
Compression libs usable with pandas serialisation: bz2, gzip, xz, zstd.
  gzip: Compressed data size: 48489691
  xz: Compressed data size: 23284368
Timings
select & fetch: 12s
decompress & deserialise: 1s
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
    """Manage cache: serialise DataFrame, compress, insert; select, decompress, deserialise to DataFrame."""

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
        """Deserialise data into a DataFrame.
        raises BadGzipFile if compression is gzip and cannot gzip
        raises UnpicklingError if cannot unpickle (after decompressing)
        raises ValueError if decompresses and deserialises to non-DataFrame"""
        kwargs.update({"compression": {"method": self.compression}})
        if self.serialisation == "csv":
            df = pd.read_csv(BytesIO(data_raw), **kwargs)
        elif self.serialisation == "pickle":
            df = pd.read_pickle(BytesIO(data_raw), **kwargs)
        if not isinstance(df, DataFrame):
            raise ValueError("Not a DataFrame")
        return df

    def _serialise(self, df: DataFrame, **kwargs) -> bytes:
        """Serialise a DataFrame."""
        kwargs.update({"compression": {"method": self.compression}})
        raw_buffer = BytesIO()
        if self.serialisation == "csv":
            df.to_csv(raw_buffer, **kwargs)
        elif self.serialisation == "pickle":
            df.to_pickle(raw_buffer, **kwargs)
        return raw_buffer.getvalue()

    def _write_to_cache_table(self, table: str, data: bytes, name: str) -> None:
        """Insert serialised, compressed data into the cache table.
        Uses upsert (on duplicate key update)."""
        df = DataFrame({"name": [name], "data": [data]})
        self.sqlahandler.to_sql(
            df, table, if_exists="append", index=False, method=SqlaHandler.upsert
        )

    def create_cache(self) -> None:
        """Create cache table."""

        logger.debug("Creating cache table.")
        Base.metadata.create_all(self.sqlahandler.engine)  # @UndefinedVariable
        logger.debug("Created cache table.")

    def delete_cache(self, name: str) -> None:
        """Delete row from cache table."""
        statement = delete(Cache).where(Cache.name == name)
        self.sqlahandler.execute(statement)

    def read_cache(self, name: str, **kwargs) -> DataFrame:
        """Select data from cache table, decompress and deserialise into DataFrame.
        Supports any sqlalchemy supported dialect and connector."""

        logger.debug("Selecting compressed, serialised data from cache table.")
        start_at = datetime.datetime.now()

        # Assemble sqlalchemy statement
        if not isinstance(name, str) and len(name) <= 100:
            raise ValueError("Suspect name: {name}")
        statement = select(Cache.data).where(Cache.name == name).limit(1)

        # Get cached data
        df = self.sqlahandler.read_sql_query(statement, **kwargs)
        if df.empty:
            raise ValueError("Data not found")
        data = df.at[0, "data"]
        logger.debug("Selected compressed, serialised data. Length: %(_len)s", {"_len": len(data)})
        end_at = datetime.datetime.now()
        duration = (end_at - start_at).total_seconds()
        logger.debug(
            "Selected and fetched data from cache table in %(duration)s s", {"duration": duration}
        )

        # Deserialise
        logger.debug("Decompressing and deserialising data to DataFrame.")
        df = self._deserialise(data)
        logger.debug(
            "Decompressed and deserialised data to DataFrame. Nrows: %(nrows)s", {"nrows": len(df)}
        )
        end_at = datetime.datetime.now()
        duration = (end_at - start_at).total_seconds()
        logger.debug(
            "Selected, decompressed and deserialised data from cache table in %(duration)s s",
            {"duration": duration},
        )
        return df

    def read_data(self, table_source: str, **kwargs) -> DataFrame:
        """Get data from cache or (failing that) from source table, update cache, return data.
        Emit warning if cannot read from cache.
        Emit warning if cannot write to cache (whilst attempting to update the cache after failing to read from it).
        """
        # Read cache
        try:
            # Read cache
            return self.read_cache(table_source)
        except ValueError as _err:
            logger.warning(
                "Key %(key)s not found in cache table: cache.",
                {"key": table_source},
            )
        except sqlalchemy.exc.ProgrammingError as _err:
            logger.warning(f"Cannot read cache table: cache: %(_err)s", {"_err": _err})
        except sqlalchemy.exc.SQLAlchemyError as _err:
            logger.exception("Unexpected SQLAlchemy error")
            raise
        except (IOError, OSError) as _err:
            logger.exception(f"Error: %(_err)s", {"_err": _err})
            raise

        # Update cache (reading from cache failed)
        logger.warning(
            "Updating cache table: cache from table_source %(table_source)s.",
            {
                "table_source": table_source,
            },
        )
        return self.update_cache(table_source, **kwargs)  # Pass exceptions up to main

    def read_table(self, table_source: str, **kwargs) -> DataFrame:
        """Select data from the source table into a Pandas DataFrame.
        Supports dialects and connectors supported by SQLAlchemy
        kwargs:
        columns:str = '*' columns to select and cache."""
        logger.debug("Selecting data from source table.")
        start_at = datetime.datetime.now()
        # Submit query
        df = self.sqlahandler.read_sql_table(table_source, **kwargs)
        end_at = datetime.datetime.now()
        duration = (end_at - start_at).total_seconds()
        logger.debug(
            "Selected and fetched data from source table into a DataFrame in %(duration)s s",
            {"duration": duration},
        )
        return df

    def update_cache(self, table_source: str, **kwargs) -> DataFrame:
        """Update cache: select, serialise, compress, insert into cache table.
        kwargs: columns: List[str]|None=None,index_col:str|None=None,parse_dates:str|None=None
        Returns df.
        """
        logger.debug("Update cache: selecting data from source table...")
        df = self.read_table(table_source, **kwargs)
        logger.debug("Update cache: selected data from source table...")
        logger.debug("Update cache: serialising, compressing, inserting")
        try:
            self.write_cache(df, table_source)
            logger.debug("Update cache: serialised, compressed, inserted")
        except sqlalchemy.exc.ProgrammingError as _err:
            logger.warning("Cannot write to cache table: cache. %(_err)s", {"_err": _err})
        return df

    def write_cache(self, df: DataFrame, name: str) -> None:
        """Cache data: serialise df, compress, insert into cache table."""
        logger.debug("Serialising and compressing DataFrame. Nrows: %(nrows)s", {"nrows": len(df)})
        data = self._serialise(df)
        logger.debug(
            "Serialised and compressed DataFrame. Data length: %(len)s",
            {"len": len(data)},
        )
        logger.debug("Inserting serialised, compressed_data.")
        self._write_to_cache_table("cache", data, name)
        logger.debug("Inserted serialised, compressed data")


class Config:
    logformat_default = "%(asctime)s %(module)s %(funcName)s %(lineno)d %(levelname)s %(message)s"
    columns_default = "id,source,source_id,longitude,latitude,install_date,dc_capacity_mwp"

    def __init__(self, config_file: Path, secrets_file: Path) -> None:
        """
        Initialise the Main class, parse configuration and set up database connection parameters.
        """
        self.config: Namespace = self._parse_config(config_file, secrets_file)
        self._setup_logging(format=self.config.logformat, level=self.config.loglevel)
        logger.debug("Compression: %(lib)s", {"lib": self.config.compression})
        logger.debug("Serialisation: %(sf)s", {"sf": self.config.serialisation})

    @staticmethod
    def _parse_config(config_file: Path, secrets_file: Path) -> Namespace:
        """Get parser with specified arguments (CLI, config, env var, default)"""
        p = configargparse.ArgParser(
            config_file_parser_class=YAMLConfigFileParser,
            default_config_files=[config_file, secrets_file],
        )
        p.add(
            "--columns",
            action="append",
            default=[],
            env_var="COLUMNS",
            help="List of columns to select from source table: default [] means all columns",
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
        p.add(
            "--index_col",
            default=None,
            env_var="INDEX_COL",
            help="Column to set as index.",
        )
        p.add_argument(
            "--loglevel",
            choices=["INFO", "WARNING", "DEBUG", "ERROR", "CRITICAL"],
            default="INFO",
            env_var="LOGLEVEL",
            help="Log level (INFO, WARNING, DEBUG etc)",
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
            help="Database port",
        )
        p.add(
            "--table_source",
            env_var="TABLE_SOURCE",
            required=True,
            help="Source database table name",
        )
        p.add("--update_cache", action="store_true", env_var="UPDATE_CACHE", help="Update cache")
        logger.debug("Parsing configuration arguments.")
        return p.parse_args()

    @staticmethod
    def _setup_logging(**kwargs) -> None:
        """Set up logging."""
        logging.basicConfig(**kwargs)


class Main:
    def __init__(self, config) -> None:
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
        """Create an instance of CacheManager."""
        return CacheManager(sqlahandler, compression=compression, serialisation=serialisation)

    @staticmethod
    def _create_sqlahandler(config: Namespace) -> SqlaHandler:
        """Create an instance of SqlaHandler."""
        mysql_overrides = SqlaHandler.get_mysql_overrides(config)
        sqla_options = SqlaHandler.get_sqla_options(config.mysql_options, mysql_overrides)
        drivername = "mysql" if (config.connector == "mysqlclient") else f"mysql+{config.connector}"
        sqla_url = SqlaHandler.get_sqla_url(sqla_options, drivername=drivername)
        engine = sqlalchemy.create_engine(sqla_url)
        logger.debug("Database connection string: %s", engine)
        return SqlaHandler(engine)

    def _create_cache_command(self):
        """Create cache table."""
        logger.debug("Creating cache table.")
        self.cache_manager.create_cache()
        logger.debug("Created cache table.")

    def _delete_cache_command(self):
        """Delete a row from the cache table."""
        logger.debug("Deleting data from cache.")
        self.cache_manager.delete_cache(self.config.table_source)
        logger.debug("Deleted data from cache.")

    def _update_cache_command(self):
        """Update the cache table with a single row of data."""
        logger.debug("Updating cache from source table.")
        self.cache_manager.update_cache(
            self.config.table_source,
            columns=self.config.columns,
            index_col=self.config.index_col,
            parse_dates=self.config.parse_dates,
        )
        logger.debug("Updated cache.")

    def _read_data_command(self):
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
        """Run: call methods given by command line (or env var) options.
        stops after the first matched command.
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

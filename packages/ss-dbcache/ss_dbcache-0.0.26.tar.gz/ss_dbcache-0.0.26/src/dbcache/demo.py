"""
Created on 6 Jul 2025

@author: ph1jb
"""

from configargparse import Namespace, YAMLConfigFileParser  # type: ignore
from pathlib import Path
import configargparse
import dbcache
import dotenv
import logging
import yaml


logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file: Path, secrets_file: Path):
        """Initialise the Main class, parse configuration and set up database connection parameters."""
        self.config: Namespace = self._parse_config(config_file, secrets_file)
        self._setup_logging(level=self.config.loglevel)

    @staticmethod
    def _parse_config(config_file: Path, secrets_file: Path) -> Namespace:
        """Get parser with specified arguments (CLI, config, env var, default)"""
        p = configargparse.ArgParser(
            config_file_parser_class=YAMLConfigFileParser,
            default_config_files=[config_file, secrets_file],
        )
        p.add(
            "--connector",
            choices=["mysqlconnector", "mysqlclient", "pymysql"],
            default="pymysql",
            env_var="CONNECTOR",
            help="MySQL connector",
        )
        p.add_argument(
            "--loglevel",
            choices=["INFO", "WARNING", "DEBUG", "ERROR", "CRITICAL"],
            default="INFO",
            env_var="LOGLEVEL",
            help="Log level (INFO, WARNING, DEBUG etc)",
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
            "--table_source",
            env_var="TABLE_SOURCE",
            required=True,
            help="Source database table name",
        )
        logger.debug("Parsing configuration arguments.")
        return p.parse_args()

    @staticmethod
    def _setup_logging(**kwargs) -> None:
        """Set up logging."""
        logging.basicConfig(**kwargs)


class Main:

    def __init__(self, config: Namespace):
        """Initialise the Main class, parse configuration and set up database connection parameters."""
        self.config = config
        self.sqlahandler = dbcache.Main._create_sqlahandler(config)
        self.cache_manager = dbcache.Main._create_cache_manager(self.sqlahandler)

    def run(self):
        self.cache_manager.read_data(self.config.table_source)


if __name__ == "__main__":
    dotenv.load_dotenv()
    CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "dbcache_config.yml"
    SECRETS_FILE = Path(__file__).resolve().parent.parent.parent / "secrets" / "dbcache_secrets.yml"
    CONFIG = Config(CONFIG_FILE, SECRETS_FILE)
    MAIN = Main(CONFIG.config)
    MAIN.run()

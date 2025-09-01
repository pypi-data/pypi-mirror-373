"""
Database Configuration Module

Uses singleton pattern to handle database configuration loading and management.
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .logger_util import logger, db_config_path

@dataclass
class DatabaseInstance:
    """Database instance configuration"""
    db_instance_id: str
    db_host: str
    db_port: int
    db_database: str
    db_username: str
    db_password: str
    db_type: str
    db_version: str
    db_active: bool


@dataclass
class DatabaseInstanceConfig:
    """Database configuration, includes connection pool settings and database instance list"""
    db_pool_size: int
    db_max_overflow: int
    db_pool_timeout: int
    db_instances_list: List[DatabaseInstance]
    log_path: str
    log_level: str


class DatabaseInstanceConfigLoader:
    """Database configuration loader, loads configuration from JSON file - Singleton pattern"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """
        Singleton pattern implementation

        Returns:
            DatabaseInstanceConfigLoader: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize configuration loader (only executed when creating instance for the first time)
        """
        if not self._initialized:
            self.config_json_file = db_config_path
            self._config: Optional[DatabaseInstanceConfig] = None
            self._initialized = True
            logger.debug(f"Database instance configuration loader initialized, configuration file: {self.config_json_file}")

    @property
    def load_config(self) -> DatabaseInstanceConfig:
        """
        Load database configuration from JSON file

        Returns:
            DatabaseInstanceConfig: Loaded configuration object

        Raises:
            FileNotFoundError: Configuration file not found
            json.JSONDecodeError: Invalid JSON format
            KeyError: Missing required configuration keys
        """
        if not os.path.exists(self.config_json_file):
            error_msg = f"Configuration file not found: {self.config_json_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(self.config_json_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.debug(f"Successfully read configuration file: {self.config_json_file}")
        except json.JSONDecodeError as e:
            error_msg = f"Configuration file JSON format error: {e}"
            logger.error(error_msg)
            raise json.JSONDecodeError(error_msg, e.doc, e.pos)

        # Validate required keys
        required_keys = ['dbList']
        for key in required_keys:
            if key not in config_data:
                error_msg = f"Missing required configuration key: {key}"
                logger.error(error_msg)
                raise KeyError(error_msg)

        # Parse database instances
        db_instances = []
        for db_data in config_data['dbList']:
            required_db_keys = [
                'dbInstanceId', 'dbHost', 'dbPort', 'dbDatabase',
                'dbUsername', 'dbPassword', 'dbType', 'dbActive'
            ]
            for key in required_db_keys:
                if key not in db_data:
                    error_msg = f"Missing required database configuration key: {key}"
                    logger.error(error_msg)
                    raise KeyError(error_msg)

            db_instance = DatabaseInstance(
                db_instance_id=db_data['dbInstanceId'],
                db_host=db_data['dbHost'],
                db_port=db_data['dbPort'],
                db_database=db_data['dbDatabase'],
                db_username=db_data['dbUsername'],
                db_password=db_data['dbPassword'],
                db_type=db_data['dbType'],
                db_version=db_data['dbVersion'],
                db_active=db_data['dbActive']
            )
            db_instances.append(db_instance)
            logger.debug(f"Parsed database instance: {db_instance.db_instance_id} ({db_instance.db_host}:{db_instance.db_port})")

        # Create configuration object
        self._config = DatabaseInstanceConfig(
            db_instances_list=db_instances,
            log_path=config_data['logPath'],
            log_level=config_data['logLevel']
        )

        logger.debug(f"Configuration loading completed, total {len(db_instances)} database instances")
        return self._config

    def get_config(self) -> DatabaseInstanceConfig:
        """
        Get loaded configuration, automatically load if not loaded

        Returns:
            DatabaseInstanceConfig: Configuration object
        """
        if self._config is None:
            return self.load_config
        return self._config

    def get_active_database(self) -> Optional[DatabaseInstance]:
        """
        Get the first active database instance

        Returns:
            Optional[DatabaseInstance]: First active database instance, returns None if no active instance found
        """
        config = self.get_config()
        for db in config.db_instances_list:
            if db.db_active:
                logger.debug(f"Found first active database: {db}")
                return db
        logger.warning("No active database instance found")
        return None


def load_db_config() -> DatabaseInstanceConfig:
    """
    Convenience function to load database configuration

    Returns:
        DatabaseInstanceConfig: Loaded configuration object
    """
    loader = DatabaseInstanceConfigLoader()
    return loader.load_config


def load_activate_db_config() -> tuple[DatabaseInstance, DatabaseInstanceConfig]:
    """
    Convenience function to load database configuration and active database instance

    Returns:
        tuple[DatabaseInstance, DatabaseInstanceConfig]: Tuple of active database instance and configuration object
    """
    loader = DatabaseInstanceConfigLoader()
    config = loader.get_config()
    active_database = loader.get_active_database()
    if active_database is None:
        raise ValueError("No active database instance found")
    return active_database, config

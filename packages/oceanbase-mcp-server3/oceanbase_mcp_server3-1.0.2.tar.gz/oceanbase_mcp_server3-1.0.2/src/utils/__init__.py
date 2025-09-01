"""
Utility Tools Module

This module contains utility functions and classes for:
- Database configuration management (JSON-based configuration with validation)
- Connection pooling (Async OceanBase connection pools for MySQL/Oracle)
- Database operations (SQL execution with transaction management)
- Logging utilities (Structured logging with file rotation)

All utilities support both  MySQL and Oracle of compatibility modes for OceanBase.
"""

from .logger_util import logger
from .db_config import (
    DatabaseInstance,
    DatabaseInstanceConfig,
    DatabaseInstanceConfigLoader,
    load_db_config,
    load_activate_db_config
)
from .db_operate import execute_sql

__all__ = [
    # Logging
    "logger",

    # Database configuration
    "DatabaseInstance",
    "DatabaseInstanceConfig",
    "DatabaseInstanceConfigLoader",
    "load_db_config",
    "load_activate_db_config",
    # Database operations
    "execute_sql",
]
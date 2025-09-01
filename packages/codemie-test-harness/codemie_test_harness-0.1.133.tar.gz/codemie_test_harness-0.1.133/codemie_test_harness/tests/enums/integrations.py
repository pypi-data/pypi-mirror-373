from enum import Enum


class DataBaseDialect(str, Enum):
    """Enum for DB Dialect names."""

    MY_SQL = "mysql"
    POSTGRES = "postgres"

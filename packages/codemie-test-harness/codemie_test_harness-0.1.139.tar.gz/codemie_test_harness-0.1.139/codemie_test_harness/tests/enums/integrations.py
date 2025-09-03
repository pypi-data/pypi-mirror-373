from enum import Enum


class DataBaseDialect(str, Enum):
    """Enum for DB Dialect names."""

    MS_SQL = "mssql"
    MY_SQL = "mysql"
    POSTGRES = "postgres"

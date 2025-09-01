from pydantic import BaseModel, Field
from typing import Generic
from .additional import AdditionalConfigT, RedisAdditionalConfig
from .connection import (
    ConnectionConfigT,
    PostgreSQLConnectionConfig,
    MySQLConnectionConfig,
    SQLiteConnectionConfig,
    SQLServerConnectionConfig,
    MongoDBConnectionConfig,
    RedisConnectionConfig,
    ElasticsearchConnectionConfig,
)
from .identifier import DatabaseIdentifierConfig
from .pooling import (
    PoolingConfigT,
    PostgreSQLPoolingConfig,
    MySQLPoolingConfig,
    SQLitePoolingConfig,
    SQLServerPoolingConfig,
    MongoDBPoolingConfig,
    RedisPoolingConfig,
    ElasticsearchPoolingConfig,
)


class BaseDatabaseConfig(
    BaseModel, Generic[ConnectionConfigT, PoolingConfigT, AdditionalConfigT]
):
    """Base configuration for database."""

    identifier: DatabaseIdentifierConfig = Field(..., description="Identifier config")
    connection: ConnectionConfigT = Field(..., description="Connection config")
    pooling: PoolingConfigT = Field(..., description="Pooling config")
    additional: AdditionalConfigT = Field(..., description="Additional config")


class PostgreSQLDatabaseConfig(
    BaseDatabaseConfig[
        PostgreSQLConnectionConfig,
        PostgreSQLPoolingConfig,
        None,
    ]
):
    additional: None = None


class MySQLDatabaseConfig(
    BaseDatabaseConfig[
        MySQLConnectionConfig,
        MySQLPoolingConfig,
        None,
    ]
):
    additional: None = None


class SQLiteDatabaseConfig(
    BaseDatabaseConfig[
        SQLiteConnectionConfig,
        SQLitePoolingConfig,
        None,
    ]
):
    additional: None = None


class SQLServerDatabaseConfig(
    BaseDatabaseConfig[
        SQLServerConnectionConfig,
        SQLServerPoolingConfig,
        None,
    ]
):
    additional: None = None


class MongoDBDatabaseConfig(
    BaseDatabaseConfig[
        MongoDBConnectionConfig,
        MongoDBPoolingConfig,
        None,
    ]
):
    additional: None = None


class RedisDatabaseConfig(
    BaseDatabaseConfig[
        RedisConnectionConfig,
        RedisPoolingConfig,
        RedisAdditionalConfig,
    ]
):
    additional: RedisAdditionalConfig = Field(..., description="Additional config")


class ElasticsearchDatabaseConfig(
    BaseDatabaseConfig[
        ElasticsearchConnectionConfig,
        ElasticsearchPoolingConfig,
        None,
    ]
):
    additional: None = None

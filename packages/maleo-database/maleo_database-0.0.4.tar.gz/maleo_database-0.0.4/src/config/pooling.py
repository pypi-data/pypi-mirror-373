from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Self, TypeVar
from maleo.types.base.dict import OptionalStringToStringDict
from maleo.types.base.integer import ListOfIntegers
from maleo.types.base.string import OptionalString
from maleo.utils.formatters.case import to_camel
from ..enums import PoolingStrategy


class BasePoolingConfig(BaseModel):
    """Base configuration class for database connection pooling."""


PoolingConfigT = TypeVar("PoolingConfigT", bound=BasePoolingConfig)


class PostgreSQLPoolingConfig(BasePoolingConfig):
    """PostgreSQL-specific pooling configuration."""

    pool_size: int = Field(
        default=10, ge=1, le=1000, description="Number of connections in the pool"
    )
    max_overflow: int = Field(
        default=20, ge=0, le=500, description="Maximum number of overflow connections"
    )
    pool_timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Timeout in seconds for getting connection",
    )
    pool_recycle: int = Field(
        default=3600, ge=60, le=86400, description="Connection recycle time in seconds"
    )
    pool_pre_ping: bool = Field(
        default=True, description="Validate connections before use"
    )
    # Keep strategy and prepared_statement_cache_size as they're pooling-related
    strategy: PoolingStrategy = Field(
        default=PoolingStrategy.DYNAMIC, description="Pooling strategy"
    )
    prepared_statement_cache_size: int = Field(
        default=100, ge=0, le=10000, description="Prepared statement cache size"
    )
    pool_reset_on_return: bool = Field(
        default=True, description="Reset connection state on return to pool"
    )

    @model_validator(mode="after")
    def validate_overflow(self) -> Self:
        if self.max_overflow > self.pool_size * 5:
            raise ValueError("max_overflow should not exceed 5x pool_size")
        return self


class MySQLPoolingConfig(BasePoolingConfig):
    """MySQL-specific pooling configuration."""

    pool_size: int = Field(
        default=8, ge=1, le=500, description="Number of connections in the pool"
    )
    max_overflow: int = Field(
        default=15, ge=0, le=200, description="Maximum number of overflow connections"
    )
    pool_timeout: float = Field(
        default=20.0,
        ge=1.0,
        le=300.0,
        description="Timeout in seconds for getting connection",
    )
    pool_recycle: int = Field(
        default=7200, ge=60, le=86400, description="Connection recycle time in seconds"
    )
    pool_pre_ping: bool = Field(
        default=True, description="Validate connections before use"
    )
    strategy: PoolingStrategy = Field(
        default=PoolingStrategy.FIXED, description="Pooling strategy"
    )
    # Add autocommit to pooling since it affects connection behavior in the pool
    autocommit: bool = Field(default=False, description="Enable autocommit mode")
    # Move connect_timeout here since it's about pool connection establishment
    connect_timeout: float = Field(
        default=10.0, ge=1.0, le=60.0, description="Connection timeout in seconds"
    )


class SQLitePoolingConfig(BasePoolingConfig):
    """SQLite-specific pooling configuration."""

    pool_size: int = Field(
        default=1, ge=1, le=10, description="Number of connections (limited for SQLite)"
    )
    max_overflow: int = Field(
        default=5, ge=0, le=20, description="Maximum overflow connections"
    )
    pool_timeout: float = Field(
        default=30.0, ge=1.0, le=300.0, description="Timeout in seconds"
    )
    # SQLite-specific pooling options
    wal_mode: bool = Field(
        default=True, description="Enable WAL mode for better concurrency"
    )
    busy_timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Busy timeout in milliseconds"
    )


class SQLServerPoolingConfig(BasePoolingConfig):
    """SQL Server-specific pooling configuration."""

    pool_size: int = Field(
        default=10, ge=1, le=500, description="Number of connections in the pool"
    )
    max_overflow: int = Field(
        default=20, ge=0, le=200, description="Maximum number of overflow connections"
    )
    pool_timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Timeout in seconds for getting connection",
    )
    pool_recycle: int = Field(
        default=3600, ge=60, le=86400, description="Connection recycle time in seconds"
    )
    pool_pre_ping: bool = Field(
        default=True, description="Validate connections before use"
    )
    strategy: PoolingStrategy = Field(
        default=PoolingStrategy.DYNAMIC, description="Pooling strategy"
    )
    # SQL Server-specific pooling settings
    connection_timeout: int = Field(
        default=30, ge=1, le=300, description="Connection timeout in seconds"
    )
    command_timeout: int = Field(
        default=30, ge=1, le=3600, description="Command timeout in seconds"
    )
    packet_size: int = Field(
        default=4096, ge=512, le=32767, description="Network packet size"
    )
    trust_server_certificate: bool = Field(
        default=False, description="Trust server certificate"
    )
    # Move encrypt here since it affects connection pool behavior
    encrypt: bool = Field(default=True, description="Encrypt connection")

    @model_validator(mode="after")
    def validate_overflow(self) -> Self:
        if self.max_overflow > self.pool_size * 3:
            raise ValueError("max_overflow should not exceed 3x pool_size")
        return self


class MongoDBPoolingConfig(BasePoolingConfig):
    """MongoDB-specific pooling configuration."""

    model_config = ConfigDict(alias_generator=to_camel)

    max_pool_size: int = Field(
        default=100, ge=1, le=500, description="Maximum number of connections in pool"
    )
    min_pool_size: int = Field(
        default=0, ge=0, le=100, description="Minimum number of connections in pool"
    )
    max_idle_time_ms: int = Field(
        default=600000, ge=1000, le=3600000, description="Max idle time in milliseconds"
    )
    connect_timeout_ms: int = Field(
        default=20000,
        ge=1000,
        le=300000,
        description="Connection timeout in milliseconds",
    )
    server_selection_timeout_ms: int = Field(
        default=30000, ge=1000, le=300000, description="Server selection timeout"
    )
    max_connecting: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Maximum number of concurrent connection attempts",
    )


class RedisPoolingConfig(BasePoolingConfig):
    """Redis-specific pooling configuration."""

    max_connections: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of connections in pool"
    )
    retry_on_timeout: bool = Field(
        default=True, description="Retry on connection timeout"
    )
    health_check_interval: int = Field(
        default=30, ge=5, le=300, description="Health check interval in seconds"
    )
    connection_timeout: float = Field(
        default=5.0, ge=1.0, le=60.0, description="Connection timeout in seconds"
    )
    socket_timeout: float = Field(
        default=5.0, ge=1.0, le=60.0, description="Socket timeout in seconds"
    )
    socket_keepalive: bool = Field(default=True, description="Enable TCP keepalive")
    decode_responses: bool = Field(
        default=True, description="Decode responses to strings"
    )


class ElasticsearchPoolingConfig(BasePoolingConfig):
    """Elasticsearch-specific pooling configuration."""

    # Connection pool settings
    maxsize: int = Field(
        default=25, ge=1, le=100, description="Maximum number of connections in pool"
    )
    connections_per_node: int = Field(
        default=10, ge=1, le=50, description="Connections per Elasticsearch node"
    )

    # Timeout settings
    timeout: float = Field(
        default=10.0, ge=1.0, le=300.0, description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum number of retries"
    )
    retry_on_timeout: bool = Field(default=False, description="Retry on timeout")
    retry_on_status: ListOfIntegers = Field(
        default_factory=lambda: [502, 503, 504],
        description="HTTP status codes to retry on",
    )

    # Connection behavior (move from connection config)
    http_compress: bool = Field(default=True, description="Enable HTTP compression")
    verify_certs: bool = Field(default=True, description="Verify SSL certificates")
    ca_certs: OptionalString = Field(
        default=None, description="Path to CA certificates"
    )

    # Advanced pool settings
    block: bool = Field(default=False, description="Block when pool is full")
    headers: OptionalStringToStringDict = Field(
        default=None, description="Default headers for requests"
    )
    dead_timeout: float = Field(
        default=60.0, ge=5.0, le=600.0, description="Dead node timeout in seconds"
    )

    @model_validator(mode="after")
    def validate_overflow(self) -> Self:
        if self.connections_per_node > self.maxsize:
            raise ValueError("connections_per_node must not exceed maxsize")
        return self

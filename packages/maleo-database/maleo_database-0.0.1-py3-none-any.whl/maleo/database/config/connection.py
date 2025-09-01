from pydantic import BaseModel, Field, model_validator
from typing import Generic, Literal, Optional, TypeVar
from urllib.parse import quote_plus, urlencode
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.dict import (
    OptionalStringToAnyDict,
    StringToAnyDict,
    StringToStringDict,
)
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import OptionalString
from ..enums import (
    Connection,
    Driver,
    PostgreSQLSSLMode,
    MySQLCharset,
    MongoDBReadPreference,
    ElasticsearchScheme,
)


DriverT = TypeVar("DriverT", bound=Driver)
UsernameT = TypeVar("UsernameT", bound=OptionalString)
PasswordT = TypeVar("PasswordT", bound=OptionalString)
HostT = TypeVar("HostT", bound=OptionalString)
PortT = TypeVar("PortT", bound=OptionalInteger)
DatabaseT = TypeVar("DatabaseT", int, str)


class BaseConnectionConfig(
    BaseModel, Generic[DriverT, UsernameT, PasswordT, HostT, PortT, DatabaseT]
):
    driver: DriverT = Field(..., description="Database's driver")
    username: UsernameT = Field(..., description="Database user's username")
    password: PasswordT = Field(
        ..., min_length=1, description="Database user's password"
    )
    host: HostT = Field(..., description="Database's host")
    port: PortT = Field(..., ge=1, le=65535, description="Database's port")
    database: DatabaseT = Field(..., description="Database's name")

    # Optional fields for different database types
    auth_source: OptionalString = Field(
        None, description="Authentication database (MongoDB)"
    )
    ssl: OptionalBoolean = Field(None, description="Enable SSL connection")
    options: OptionalStringToAnyDict = Field(
        default_factory=dict, description="Additional connection options"
    )

    @model_validator(mode="after")
    def validate_required_fields_per_driver(self):
        """Validate that required fields are present based on driver type"""
        if self.driver is Driver.SQLITE:
            if not self.database:
                raise ValueError("SQLite requires database file path")
        elif self.driver in [
            Driver.POSTGRESQL,
            Driver.MYSQL,
            Driver.MSSQL,
        ]:
            if not self.host:
                raise ValueError(f"{self.driver} requires host")
            if not self.username:
                raise ValueError(f"{self.driver} requires username")
            if not self.password:
                raise ValueError(f"{self.driver} requires password")
        elif self.driver is Driver.REDIS:
            if not self.host:
                raise ValueError("Redis requires host")
        elif self.driver is Driver.MONGODB:
            if not self.host:
                raise ValueError("MongoDB requires host")

        return self

    def _safe_encode_credential(self, credential: OptionalString) -> str:
        """Safely URL-encode credentials to handle special characters."""
        return quote_plus(credential) if credential else ""

    def _make_options_string(
        self, additional_options: OptionalStringToAnyDict = None
    ) -> str:
        """Build URL query string from options, removing null values."""
        all_options: StringToAnyDict = dict(self.options) if self.options else {}
        if additional_options:
            all_options.update(additional_options)

        # Filter out None values
        all_options = {k: v for k, v in all_options.items() if v is not None}

        if not all_options:
            return ""

        # Convert boolean values to lowercase strings
        formatted_options = {
            k: str(v).lower() if isinstance(v, bool) else str(v)
            for k, v in all_options.items()
        }

        return "?" + urlencode(formatted_options)

    def make_async_url(self) -> str:
        return self.make_url(Connection.ASYNC)

    def make_sync_url(self) -> str:
        return self.make_url(Connection.SYNC)

    def make_url(self, connection: Connection = Connection.ASYNC) -> str:
        """Build URL based on driver-specific format with async/sync support."""
        if self.driver is Driver.POSTGRESQL:
            return self._make_postgresql_url(connection)
        elif self.driver is Driver.MYSQL:
            return self._make_mysql_url(connection)
        elif self.driver is Driver.SQLITE:
            return self._make_sqlite_url(connection)
        elif self.driver is Driver.MONGODB:
            return self._make_mongodb_url()
        elif self.driver is Driver.REDIS:
            return self._make_redis_url()
        elif self.driver is Driver.MSSQL:
            return self._make_mssql_url(connection)
        elif self.driver is Driver.ELASTICSEARCH:
            return self._make_elasticsearch_url()
        else:
            # Fallback to standard format
            encoded_user = self._safe_encode_credential(self.username)
            encoded_pass = self._safe_encode_credential(self.password)
            return f"{self.driver}://{encoded_user}:{encoded_pass}@{self.host}:{self.port}/{self.database}"

    def _make_postgresql_url(self, connection: Connection = Connection.ASYNC) -> str:
        """PostgreSQL database URL format with proper async/sync drivers."""
        raise NotImplementedError()

    def _make_mysql_url(self, connection: Connection = Connection.ASYNC) -> str:
        """MySQL database URL format with proper async/sync drivers."""
        raise NotImplementedError()

    def _make_sqlite_url(self, connection: Connection = Connection.ASYNC) -> str:
        """SQLite URL format with async/sync support."""
        raise NotImplementedError()

    def _make_mongodb_url(self) -> str:
        """MongoDB URL format - MongoDB driver handles async/sync internally."""
        raise NotImplementedError()

    def _make_redis_url(self) -> str:
        """Redis URL format with async/sync support."""
        raise NotImplementedError()

    def _make_mssql_url(self, connection: Connection = Connection.ASYNC) -> str:
        """SQL Server URL format with async/sync drivers."""
        raise NotImplementedError()

    def _make_elasticsearch_url(self) -> str:
        """Elasticsearch URL format - HTTP-based, same for async/sync."""
        raise NotImplementedError()

    def get_driver_variants(self) -> StringToStringDict:
        """Get available driver variants for this database type."""
        variants = {}

        if self.driver is Driver.POSTGRESQL:
            variants.update(
                {
                    "async": "postgresql+asyncpg",
                    "sync": "postgresql+psycopg2",
                    "sync_alt": "postgresql+pg8000",
                }
            )
        elif self.driver is Driver.MYSQL:
            variants.update(
                {
                    "async": "mysql+aiomysql",
                    "sync": "mysql+pymysql",
                    "sync_alt": "mysql+mysqlclient",
                }
            )
        elif self.driver is Driver.SQLITE:
            variants.update({"async": "sqlite+aiosqlite", "sync": "sqlite"})
        elif self.driver is Driver.MSSQL:
            variants.update(
                {
                    "async": "mssql+aioodbc",
                    "sync": "mssql+pyodbc",
                    "sync_alt": "mssql+pymssql",
                }
            )
        elif self.driver is Driver.MONGODB:
            variants.update({"async": "mongodb (motor)", "sync": "mongodb (pymongo)"})
        elif self.driver is Driver.REDIS:
            variants.update({"async": "redis (aioredis)", "sync": "redis (redis-py)"})
        elif self.driver is Driver.ELASTICSEARCH:
            variants.update(
                {
                    "async": "elasticsearch (elasticsearch-async)",
                    "sync": "elasticsearch (elasticsearch-py)",
                }
            )

        return variants

    def make_url_with_custom_driver(self, driver_string: str) -> str:
        """Build URL with a custom driver string (useful for specific driver variants)."""
        if self.driver in [Driver.SQLITE]:
            return f"{driver_string}:///{self.database}" + self._make_options_string()
        elif self.driver in [Driver.REDIS]:
            auth_part = ""
            if self.username and self.password:
                encoded_user = self._safe_encode_credential(self.username)
                encoded_pass = self._safe_encode_credential(self.password)
                auth_part = f"{encoded_user}:{encoded_pass}@"
            elif self.password:
                encoded_pass = self._safe_encode_credential(self.password)
                auth_part = f":{encoded_pass}@"
            return (
                f"{driver_string}://{auth_part}{self.host}:{self.port}/{self.database}"
                + self._make_options_string()
            )
        elif self.driver in [Driver.ELASTICSEARCH]:
            scheme = getattr(self, "scheme", "http")
            auth_part = ""
            if self.username and self.password:
                encoded_user = self._safe_encode_credential(self.username)
                encoded_pass = self._safe_encode_credential(self.password)
                auth_part = f"{encoded_user}:{encoded_pass}@"
            return (
                f"{scheme}://{auth_part}{self.host}:{self.port}"
                + self._make_options_string()
            )
        else:
            # Standard SQL databases
            encoded_user = self._safe_encode_credential(self.username)
            encoded_pass = self._safe_encode_credential(self.password)
            return (
                f"{driver_string}://{encoded_user}:{encoded_pass}@{self.host}:{self.port}/{self.database}"
                + self._make_options_string()
            )


ConnectionConfigT = TypeVar("ConnectionConfigT", bound=BaseConnectionConfig)


class PostgreSQLConnectionConfig(
    BaseConnectionConfig[Literal[Driver.POSTGRESQL], str, str, str, int, str]
):
    driver: Literal[Driver.POSTGRESQL] = Driver.POSTGRESQL
    port: int = Field(5432, description="PostgreSQL port")
    username: str = Field("postgres", description="PostgreSQL username")

    # PostgreSQL-specific options
    echo: bool = Field(False, description="Enable SQL statement logging")
    sslmode: Optional[PostgreSQLSSLMode] = Field(None, description="SSL mode")
    application_name: OptionalString = Field(
        None, description="Application name for connection tracking"
    )

    def _make_postgresql_url(self, connection: Connection = Connection.ASYNC) -> str:
        """PostgreSQL database URL format with proper async/sync drivers."""
        # Choose appropriate driver based on connection type
        if connection is Connection.ASYNC:
            driver_name = "postgresql+asyncpg"
        elif connection is Connection.SYNC:
            driver_name = "postgresql+psycopg2"
        else:
            driver_name = "postgresql"  # Default

        encoded_user = self._safe_encode_credential(self.username)
        encoded_pass = self._safe_encode_credential(self.password)

        base_url = f"{driver_name}://{encoded_user}:{encoded_pass}@{self.host}:{self.port}/{self.database}"

        # Add PostgreSQL-specific options
        pg_options = {
            "echo": self.echo,
            "sslmode": self.sslmode,
            "application_name": self.application_name,
        }

        return base_url + self._make_options_string(pg_options)


class MySQLConnectionConfig(
    BaseConnectionConfig[Literal[Driver.MYSQL], str, str, str, int, str]
):
    driver: Literal[Driver.MYSQL] = Driver.MYSQL
    port: int = Field(3306, description="MySQL port")
    username: str = Field("root", description="MySQL username")

    # MySQL-specific options
    echo: bool = Field(False, description="Enable SQL statement logging")
    charset: MySQLCharset = Field(MySQLCharset.UTF8MB4, description="Character set")

    def _make_mysql_url(self, connection: Connection = Connection.ASYNC) -> str:
        """MySQL database URL format with proper async/sync drivers."""
        # Choose appropriate driver based on connection type
        if connection is Connection.ASYNC:
            driver_name = "mysql+aiomysql"
        elif connection is Connection.SYNC:
            driver_name = "mysql+pymysql"  # or mysqlclient
        else:
            driver_name = "mysql"  # Default

        encoded_user = self._safe_encode_credential(self.username)
        encoded_pass = self._safe_encode_credential(self.password)

        base_url = f"{driver_name}://{encoded_user}:{encoded_pass}@{self.host}:{self.port}/{self.database}"

        # Add MySQL-specific options
        mysql_options = {"charset": self.charset}
        return base_url + self._make_options_string(mysql_options)


class SQLiteConnectionConfig(
    BaseConnectionConfig[Literal[Driver.SQLITE], None, None, None, None, str]
):
    driver: Literal[Driver.SQLITE] = Driver.SQLITE
    database: str = Field(..., min_length=1, description="SQLite database file path")

    # SQLite doesn't need these fields
    username: None = Field(None, description="Not used in SQLite")
    password: None = Field(None, description="Not used in SQLite")
    host: None = Field(None, description="Not used in SQLite")
    port: None = Field(None, description="Not used in SQLite")

    echo: bool = Field(False, description="Enable SQL statement logging")

    def _make_sqlite_url(self, connection: Connection = Connection.ASYNC) -> str:
        """SQLite URL format with async/sync support."""
        # SQLite async/sync drivers
        if connection is Connection.ASYNC:
            driver_name = "sqlite+aiosqlite"
        elif connection is Connection.SYNC:
            driver_name = "sqlite"
        else:
            driver_name = "sqlite"  # Default to sync

        # For SQLite, database field contains the file path
        base_url = f"{driver_name}:///{self.database}"
        return base_url + self._make_options_string()


class SQLServerConnectionConfig(
    BaseConnectionConfig[Literal[Driver.MSSQL], str, str, str, int, str]
):
    driver: Literal[Driver.MSSQL] = Driver.MSSQL
    port: int = Field(1433, description="SQL Server port")

    # SQL Server-specific options
    echo: bool = Field(False, description="Enable SQL statement logging")
    odbc_driver: str = Field(
        "ODBC Driver 17 for SQL Server", description="ODBC driver name"
    )
    trusted_connection: bool = Field(False, description="Use Windows Authentication")

    @model_validator(mode="after")
    def validate_auth_method(self):
        """Validate authentication method consistency"""
        if self.trusted_connection:
            # Windows auth doesn't need username/password
            if self.username or self.password:
                raise ValueError(
                    "Username/password not needed with trusted_connection=True"
                )
        else:
            # SQL auth requires username/password
            if not self.username or not self.password:
                raise ValueError(
                    "Username and password required when trusted_connection=False"
                )
        return self

    def _make_mssql_url(self, connection: Connection = Connection.ASYNC) -> str:
        """SQL Server URL format with async/sync drivers."""
        # Choose appropriate driver based on connection type
        if connection is Connection.ASYNC:
            driver_name = "mssql+aioodbc"  # or mssql+asyncpg for some setups
        elif connection is Connection.SYNC:
            driver_name = "mssql+pyodbc"
        else:
            driver_name = "mssql+pyodbc"  # Default to sync

        encoded_user = self._safe_encode_credential(self.username)
        encoded_pass = self._safe_encode_credential(self.password)

        base_url = f"{driver_name}://{encoded_user}:{encoded_pass}@{self.host}:{self.port}/{self.database}"

        # Add SQL Server-specific options
        mssql_options = {
            "driver": self.odbc_driver,
            "trusted_connection": "yes" if self.trusted_connection else "no",
        }
        return base_url + self._make_options_string(mssql_options)


class MongoDBConnectionConfig(
    BaseConnectionConfig[
        Literal[Driver.MONGODB], OptionalString, OptionalString, str, int, str
    ]
):
    driver: Literal[Driver.MONGODB] = Driver.MONGODB
    port: int = Field(27017, description="MongoDB port")
    username: OptionalString = Field(None, description="MongoDB username")
    password: OptionalString = Field(None, description="MongoDB password")

    # MongoDB-specific options
    auth_source: OptionalString = Field("admin", description="Authentication database")
    replica_set: OptionalString = Field(None, description="Replica set name")
    read_preference: Optional[MongoDBReadPreference] = Field(
        MongoDBReadPreference.PRIMARY, description="Read preference"
    )

    @model_validator(mode="after")
    def validate_auth_consistency(self):
        """Both username and password should be provided together"""
        if (self.username is None) != (self.password is None):
            raise ValueError(
                "Username and password must both be provided or both be None"
            )
        return self

    def _make_mongodb_url(self) -> str:
        """MongoDB URL format - MongoDB driver handles async/sync internally."""
        # MongoDB uses the same URL format for both async and sync
        # The async/sync behavior is determined by the client library used

        auth_part = ""
        if self.username and self.password:
            encoded_user = self._safe_encode_credential(self.username)
            encoded_pass = self._safe_encode_credential(self.password)
            auth_part = f"{encoded_user}:{encoded_pass}@"

        base_url = f"mongodb://{auth_part}{self.host}:{self.port}/{self.database}"

        # Add MongoDB-specific options
        mongo_options = {
            "authSource": self.auth_source,
            "replicaSet": self.replica_set,
            "readPreference": self.read_preference,
            "ssl": self.ssl,
        }
        return base_url + self._make_options_string(mongo_options)


class RedisConnectionConfig(
    BaseConnectionConfig[
        Literal[Driver.REDIS], OptionalString, OptionalString, str, int, int
    ]
):
    driver: Literal[Driver.REDIS] = Driver.REDIS
    port: int = Field(6379, description="Redis port")
    database: int = Field(0, ge=0, le=15, description="Redis database number (0-15)")
    username: OptionalString = Field(None, description="Redis username (Redis 6+)")
    password: OptionalString = Field(None, description="Redis password")

    # Redis-specific options
    decode_responses: bool = Field(True, description="Decode responses to strings")
    max_connections: Optional[int] = Field(
        None, ge=1, description="Max connections in pool"
    )

    def _make_redis_url(self) -> str:
        """Redis URL format with async/sync support."""
        # Redis URL format is the same, but different libraries handle async/sync
        # redis-py for sync, aioredis for async

        auth_part = ""
        if self.username and self.password:
            encoded_user = self._safe_encode_credential(self.username)
            encoded_pass = self._safe_encode_credential(self.password)
            auth_part = f"{encoded_user}:{encoded_pass}@"
        elif self.password:
            encoded_pass = self._safe_encode_credential(self.password)
            auth_part = f":{encoded_pass}@"

        base_url = f"redis://{auth_part}{self.host}:{self.port}/{self.database}"

        # Add Redis-specific options
        redis_options = {"decode_responses": self.decode_responses}
        return base_url + self._make_options_string(redis_options)


class ElasticsearchConnectionConfig(
    BaseConnectionConfig[
        Literal[Driver.ELASTICSEARCH], OptionalString, OptionalString, str, int, str
    ]
):
    driver: Literal[Driver.ELASTICSEARCH] = Driver.ELASTICSEARCH
    port: int = Field(9200, description="Elasticsearch port")
    username: OptionalString = Field(None, description="Elasticsearch username")
    password: OptionalString = Field(None, description="Elasticsearch password")
    database: str = Field("_all", description="Elasticsearch index pattern")

    # Elasticsearch-specific options
    scheme: ElasticsearchScheme = Field(
        ElasticsearchScheme.HTTP, description="Connection scheme (http/https)"
    )

    @model_validator(mode="after")
    def validate_https_consistency(self):
        """Validate HTTPS and SSL consistency"""
        if self.scheme == "https" and self.ssl is False:
            raise ValueError("Cannot use https scheme with ssl=False")
        return self

    def _make_elasticsearch_url(self) -> str:
        """Elasticsearch URL format - HTTP-based, same for async/sync."""
        # Elasticsearch uses HTTP/HTTPS, async/sync is handled by the client library

        auth_part = ""

        if self.username and self.password:
            encoded_user = self._safe_encode_credential(self.username)
            encoded_pass = self._safe_encode_credential(self.password)
            auth_part = f"{encoded_user}:{encoded_pass}@"

        base_url = f"{self.scheme}://{auth_part}{self.host}:{self.port}"

        # Elasticsearch doesn't typically use database in URL path like SQL databases
        # The 'database' field might represent default index, but it's usually specified per request

        # Add Elasticsearch-specific options as URL params if needed
        es_options = {}
        return base_url + self._make_options_string(es_options)


# Factory function with better type hints
def create_connection_config(driver: Driver, **kwargs) -> BaseConnectionConfig:
    """Factory to create the appropriate connection config based on driver"""
    config_map = {
        Driver.POSTGRESQL: PostgreSQLConnectionConfig,
        Driver.MYSQL: MySQLConnectionConfig,
        Driver.SQLITE: SQLiteConnectionConfig,
        Driver.MONGODB: MongoDBConnectionConfig,
        Driver.REDIS: RedisConnectionConfig,
        Driver.MSSQL: SQLServerConnectionConfig,
        Driver.ELASTICSEARCH: ElasticsearchConnectionConfig,
    }

    config_class = config_map.get(driver)
    if not config_class:
        raise ValueError(f"Unsupported driver: {driver}")

    return config_class(driver=driver, **kwargs)

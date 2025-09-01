from enum import StrEnum


class Connection(StrEnum):
    ASYNC = "async"
    SYNC = "sync"


class Driver(StrEnum):
    # SQL Databases - Most Popular
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

    # SQL Databases - Enterprise
    # ORACLE = "oracle"
    MSSQL = "mssql"  # SQL Server
    # MARIADB = "mariadb"

    # NoSQL Document Stores
    MONGODB = "mongodb"
    # COUCHDB = "couchdb"

    # NoSQL Key-Value
    REDIS = "redis"
    # DYNAMODB = "dynamodb"  # AWS

    # NoSQL Column Family
    # CASSANDRA = "cassandra"
    # HBASE = "hbase"

    # NoSQL Graph
    # NEO4J = "neo4j"
    # ARANGODB = "arangodb"

    # Time Series
    # INFLUXDB = "influxdb"
    # TIMESCALEDB = "timescaledb"  # PostgreSQL extension

    # In-Memory
    # MEMCACHED = "memcached"

    # Search Engines
    ELASTICSEARCH = "elasticsearch"
    # OPENSEARCH = "opensearch"

    # Cloud Native
    # FIRESTORE = "firestore"  # Google
    # COSMOSDB = "cosmosdb"  # Azure


class PostgreSQLSSLMode(StrEnum):
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"


class MySQLCharset(StrEnum):
    UTF8 = "utf8"
    UTF8MB4 = "utf8mb4"
    LATIN1 = "latin1"
    ASCII = "ascii"


class MongoDBReadPreference(StrEnum):
    PRIMARY = "primary"
    PRIMARY_PREFERRED = "primaryPreferred"
    SECONDARY = "secondary"
    SECONDARY_PREFERRED = "secondaryPreferred"
    NEAREST = "nearest"


class ElasticsearchScheme(StrEnum):
    HTTP = "http"
    HTTPS = "https"


class PoolingStrategy(StrEnum):
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    OVERFLOW = "overflow"
    QUEUE = "queue"

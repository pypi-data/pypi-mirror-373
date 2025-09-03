snowflake_to_system = {
    # basic types
    "INT": "integer",
    "INTEGER": "integer",
    "BIGINT": "integer",
    "FLOAT": "double",
    "DECIMAL": "numeric",
    "DOUBLE": "double",
    "DOUBLE PRECISION": "double",
    "REAL": "real",
    "STRING": "string",
    "VARCHAR": "string",
    "BINARY": "binary",
    "BOOLEAN": "boolean",
    "TIMESTAMP": "timestamp",

    # additional numeric types
    "NUMBER": "numeric",
    "NUMERIC": "numeric",
    "SMALLINT": "integer",
    "TINYINT": "integer",
    "BYTEINT": "integer",
    "FLOAT4": "double",
    "FLOAT8": "double",

    # additional string types
    "CHAR": "string",
    "CHARACTER": "string",
    "TEXT": "string",

    # additional temporal types
    "DATE": "date",
    "DATETIME": "timestamp",
    "TIME": "timestamp",
    "TIMESTAMP_LTZ": "timestamp",
    "TIMESTAMP_NTZ": "timestamp",
    "TIMESTAMP_TZ": "timestamp",

    # additional binary types
    "VARBINARY": "binary",

    # geospatial types
    "GEOMETRY": "geometry",
    "GEOGRAPHY": "geography",

    # Other specific types
    "INTERVAL": "interval",
    "VARIANT": "json",
    "OBJECT": "json",
    "ARRAY": "array",
    "MAP": "map",
    "VECTOR": "vector",
    "UUID": "string",
    "NULL": "null",
}

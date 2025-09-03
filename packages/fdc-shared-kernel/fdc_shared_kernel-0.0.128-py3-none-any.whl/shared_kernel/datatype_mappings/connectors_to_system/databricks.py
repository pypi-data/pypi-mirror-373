databricks_to_system = {
    # basic types
    "INT": "integer",
    "BIGINT": "integer",
    "BINARY": "binary",
    "BOOLEAN": "boolean",
    "STRING": "string",
    "VARCHAR": "string",
    "DATE": "date",
    "DECIMAL": "numeric",
    "DOUBLE": "double",
    "FLOAT": "real",
    "TIMESTAMP": "timestamp",
    "TIMESTAMP_NTZ": "timestamp",

    # additional numeric types
    "SMALLINT": "integer",
    "TINYINT": "integer",

    # additional string types
    "CHAR": "string",

    # Other specific types
    "INTERVAL": "interval",
    "VOID": "null",
    "ARRAY": "array",
    "MAP": "map",
    "STRUCT": "struct",
    "VARIANT": "json",
    "OBJECT": "json",
    "UUID": "string",
    "NULL": "null",
}

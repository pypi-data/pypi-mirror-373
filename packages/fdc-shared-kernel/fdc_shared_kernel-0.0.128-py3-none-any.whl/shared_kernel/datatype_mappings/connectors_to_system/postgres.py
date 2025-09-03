postgres_to_system = {
    # Integer types
    "BIGINT": "integer",
    "BIGSERIAL": "integer",
    "SMALLINT": "integer",
    "INTEGER": "integer",
    "INT": "integer",
    "SERIAL": "integer",
    "SMALLSERIAL": "integer",

    # Boolean
    "BOOLEAN": "boolean",
    "BOOL": "boolean",

    # Numeric / Decimal
    "NUMERIC": "numeric",
    "DECIMAL": "numeric",
    "MONEY": "numeric",

    # Floating-point
    "REAL": "real",
    "FLOAT4": "real",
    "DOUBLE PRECISION": "double",
    "FLOAT8": "double",

    # Character types
    "CHARACTER VARYING": "string",
    "VARCHAR": "string",
    "CHARACTER": "string",
    "CHAR": "string",
    "TEXT": "string",

    # Binary
    "BYTEA": "binary",

    # Date/Time
    "DATE": "date",
    "TIME": "timestamp",
    "TIMETZ": "timestamp",
    "TIME WITH TIME ZONE": "timestamp",
    "TIME WITHOUT TIME ZONE": "timestamp",
    "TIMESTAMP": "timestamp",
    "TIMESTAMP WITHOUT TIME ZONE": "timestamp",
    "TIMESTAMP WITH TIME ZONE": "timestamp",
    "TIMESTAMPTZ": "timestamp",
    "INTERVAL": "interval",

    # JSON
    "JSON": "json",
    "JSONB": "json",

    # Network types
    "INET": "string",
    "CIDR": "string",
    "MACADDR": "string",
    "MACADDR8": "string",

    # Geometric types
    "POINT": "geometry",
    "LINE": "geometry",
    "LSEG": "geometry",
    "BOX": "geometry",
    "PATH": "geometry",
    "POLYGON": "geometry",
    "CIRCLE": "geometry",

    # Full-text search
    "TSVECTOR": "string",
    "TSQUERY": "string",

    # System types
    "PG_LSN": "string",
    "TXID_SNAPSHOT": "string",
    "PG_SNAPSHOT": "string",

    # Others
    "BIT": "bit",
    "BIT VARYING": "bit",
    "NULL": "null",
    "UUID": "string",
    "XML": "xml",
}

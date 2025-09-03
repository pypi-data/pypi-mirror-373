redshift_to_system = {
    # basic types
    "BIGINT": "integer",
    "INTEGER": "integer",
    "REAL": "real",
    "DECIMAL": "numeric",
    "DOUBLE PRECISION": "double",
    "BOOLEAN": "boolean",
    "VARBYTE": "binary",
    "VARCHAR": "string",
    "CHARACTER VARYING": "string",
    "DATE": "date",
    "TIMESTAMPTZ": "timestamp",
    "TIMESTAMP WITH TIME ZONE": "timestamp",
    "TIMESTAMP": "timestamp",
    "SMALLINT": "integer",
    "NULL": "null",
    "NONE": "null",
    
    # additional numeric types
    "NUMERIC": "numeric",
    "FLOAT": "double",
    "FLOAT4": "real",
    "FLOAT8": "double",
    "INT": "integer",
    "INT2": "integer",
    "INT4": "integer",
    "INT8": "integer",
    
    # additional string types
    "CHAR": "string",
    "CHARACTER": "string",
    "NCHAR": "string",
    "NVARCHAR": "string",
    "TEXT": "string",
    "BPCHAR": "string",  # blank-padded CHAR
    
    # additional temporal types
    "TIME": "timestamp",
    "TIMETZ": "timestamp",
    "TIME WITH TIME ZONE": "timestamp",
    "TIMESTAMP WITHOUT TIME ZONE": "timestamp",
    
    # additional binary types
    "BYTEA": "binary",
    "RAW": "binary",
    
    # array types
    "ARRAY": "array",
    
    # semi-structured types
    "JSON": "json",
    "JSONB": "json",
    "SUPER": "json",  # redshift SUPER type
    
    # geospatial types
    "GEOMETRY": "geometry",
    "GEOGRAPHY": "geography",
    
    # Other specific types
    "HLLSKETCH": "binary",  # hyperLogLog sketch
    "UUID": "string",
    "INTERVAL": "interval",
    "CIDR": "string",
    "INET": "string",
    "MACADDR": "string",
    "REGCLASS": "string",
    "OID": "integer"
}
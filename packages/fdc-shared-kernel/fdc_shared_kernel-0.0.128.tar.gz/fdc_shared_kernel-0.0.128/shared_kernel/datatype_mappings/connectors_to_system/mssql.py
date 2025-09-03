mssql_to_system = {
    # basic types
    "TINYINT": "integer",
    "SMALLINT": "integer",
    "INT": "integer",
    "BIGINT": "integer",
    "BIT": "boolean",
    "DECIMAL": "numeric",
    "NUMERIC": "numeric",
    "FLOAT": "double",
    "REAL": "real",
    "VARCHAR": "string",
    "TEXT": "string",
    "DATE": "date",
    "TIME": "timestamp",
    "BINARY": "binary",
    "TIMESTAMP": "timestamp",

    # additional numeric types
    "MONEY": "numeric",
    "SMALLMONEY": "numeric",

    # additional string types
    "CHAR": "string",
    "NCHAR": "string",
    "NVARCHAR": "string",
    "NTEXT": "string",

    # additional temporal types
    "DATETIME": "datetime",
    "SMALLDATETIME": "datetime",
    "DATETIME2": "datetime",
    "DATETIMEOFFSET": "datetime",

    # additional binary types
    "VARBINARY": "binary",

    # other specific types
    "CURSOR": "cursor",
    "GEOGRAPHY": "geography",
    "GEOMETRY": "geometry",
    "HIERARCHYID": "hierarchyid",
    "JSON": "json",
    "VECTOR": "vector",
    "ROWVERSION": "rowversion",
    "SQL_VARIANT": "variant",
    "TABLE": "table",
    "UNIQUEIDENTIFIER": "string",
    "UUID": "string",
    "XML": "xml",
    "NULL": "null",
}

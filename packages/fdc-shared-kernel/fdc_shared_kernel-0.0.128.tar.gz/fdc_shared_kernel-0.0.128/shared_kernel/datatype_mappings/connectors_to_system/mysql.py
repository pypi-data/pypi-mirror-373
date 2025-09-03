mysql_to_system = {
    # String Data Types
    "CHAR": "string",
    "VARCHAR": "string",
    "BINARY": "binary",
    "VARBINARY": "binary",
    "TINYBLOB": "binary",
    "TINYTEXT": "string",
    "TEXT": "string",
    "BLOB": "binary",
    "MEDIUMTEXT": "string",
    "MEDIUMBLOB": "binary",
    "LONGTEXT": "string",
    "LONGBLOB": "binary",
    "ENUM": "string",
    "SET": "array",

    # Numeric Data Types
    "BIT": "bit",
    "TINYINT": "integer",
    "BOOL": "boolean",
    "BOOLEAN": "boolean",
    "SMALLINT": "integer",
    "MEDIUMINT": "integer",
    "INT": "integer",
    "INTEGER": "integer",
    "BIGINT": "integer",
    "FLOAT": "double",
    "DOUBLE": "double",
    "DOUBLE PRECISION": "double",
    "DECIMAL": "numeric",
    "DEC": "numeric",
    "NUMERIC": "numeric",

    # Date and Time Data Types
    "DATE": "date",
    "DATETIME": "datetime",
    "TIMESTAMP": "timestamp",
    "TIME": "timestamp",
    "YEAR": "integer",

    # Other Specific Types
    "NULL": "null",
    "UUID": "string",
    "JSON": "json",
    "XML": "xml",
}

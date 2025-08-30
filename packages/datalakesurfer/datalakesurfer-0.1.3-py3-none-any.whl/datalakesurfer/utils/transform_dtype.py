from typing import Dict, List, Any
import re

class MapDataType:

    def __init__(self):
        self.DATA_TYPE_MAPPINGS = {
            "iceberg": {
                "string": ["VARCHAR","UUID","TIME","JSON","INTERVAL","BIT","BLOB"],
                "boolean": ["BOOLEAN"],
                "smallint": ["SMALLINT", "USMALLINT"],
                "int": ["INTEGER", "UINTEGER"],
                "bigint": ["HUGEINT", "BIGINT", "UBIGINT", "UHUGEINT"],
                "tinyint": ["TINYINT", "UTINYINT"],
                "float": ["FLOAT"],
                "double": ["DOUBLE"],
                "decimal(38,18)": ["DECIMAL", "NUMERIC"],
                "date": ["DATE"],
                "timestamp": ["TIMESTAMP", "TIMESTAMPTZ"]
            },
            "parquet": {
                "string": ["STRING", "LARGE_STRING", "UTF8","INTERVAL","BINARY"],
                "boolean": ["BOOL","BOOLEAN"],
                "byte": ["INT8", "UINT8"],
                "short": ["INT16", "UINT16"],
                "int": ["INT32", "UINT32"],
                "long": ["INT64", "UINT64", "LONG"],
                "float": ["FLOAT16", "FLOAT32", "HALFFLOAT", "FLOAT"],
                "double": ["FLOAT64", "DOUBLE"],
                "decimal(38,18)": ["DECIMAL","DECIMAL128", "DECIMAL256"],
                "date": ["DATE","DATE32", "DATE64"],
                "timestamp": [
                    "TIMESTAMP","TIMESTAMP[NS]", "TIMESTAMP[US]", "TIMESTAMP[MS]", "TIMESTAMP[S]",
                    "TIMESTAMP[NS, TZ=UTC]", "TIMESTAMP[US, TZ=UTC]", "TIMESTAMP[MS, TZ=UTC]", "TIMESTAMP[S, TZ=UTC]"
                ]
            },
            "delta": {
                "string": ["STRING", "VARCHAR", "CHAR","INTERVAL", "BINARY"],
                "boolean": ["BOOLEAN"],
                "byte": ["BYTE", "TINYINT"],
                "short": ["SHORT", "SMALLINT"],
                "int": ["INT", "INTEGER"],
                "long": ["BIGINT", "LONG"],
                "float": ["FLOAT"],
                "double": ["DOUBLE"],
                "decimal(38,18)": ["DECIMAL"],
                "date": ["DATE"],
                "timestamp": ["TIMESTAMP","TIMESTAMP_NTZ"]
            }
        }

    def fnMapDataType(self, schema_list: List[Dict[str, str]], sourceType: str = "iceberg") -> Dict[str, Any]:
        mapped_schema = []
        type_mapping = self.DATA_TYPE_MAPPINGS.get(sourceType.lower())
        if not type_mapping:
            raise ValueError(f"Unsupported source type: {sourceType}")
        for column in schema_list:
            column_name = column.get("column_name", "").strip()
            dtype_raw = column.get("dtype", "").strip().upper()
            if not column_name or not dtype_raw:
                raise ValueError(f"Invalid schema column definition: {column}")
            # Extract base type
            dtype_match = re.match(r"^([A-Z0-9_]+)", dtype_raw, re.IGNORECASE)
            if dtype_match:
                dtype = dtype_match.group(1)
            else:
                raise ValueError(f"Invalid data type '{dtype_raw}' for column '{column_name}'.")
            source_column = {"column_name": column_name}
            # Map to Spark type
            for spark_type, source_types in type_mapping.items():
                if dtype in source_types:
                    source_column["dtype"] = spark_type
                    # Decimal: try to parse precision and scale from original string
                    if spark_type.startswith("decimal"):
                        match = re.search(r"\((\d+)\s*,\s*(\d+)\)", dtype_raw)
                        if match:
                            precision, scale = int(match.group(1)), int(match.group(2))
                        else:
                            precision, scale = 38, 18
                        source_column["typeproperties"] = {"precision": precision, "scale": scale}
                    break
            else:
                raise ValueError(
                    f"Unsupported data type '{dtype}' for column '{column_name}' in source '{sourceType}'."
                )
            mapped_schema.append(source_column)
        return {"status": "success", "schema": mapped_schema}

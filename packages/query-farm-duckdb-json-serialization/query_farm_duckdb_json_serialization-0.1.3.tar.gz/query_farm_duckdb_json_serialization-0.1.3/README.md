# query-farm-duckdb-json-serialization

This Python module provides a [Pydantic](https://docs.pydantic.dev/) parser for [DuckDB](https://duckdb.org) expressions that have been serialized to JSON by the [Airport](https://airport.query.farm) DuckDB extension.

These expressions are used by Apache Arrow Flight servers to perform **predicate pushdown** — enabling the server to filter rows efficiently before sending data to the client.

## Purpose

The module's primary function is to:

- **Parse** DuckDB expressions serialized as JSON.
- **Optionally convert** the parsed expressions back into SQL.
- Allow **server-side row filtering** using DuckDB, before returning data via Arrow Flight.

> **Note**: The JSON format used by [Airport](https://airport.query.farm) differs from the built-in DuckDB JSON serialization. Specifically, binary values are encoded using **Base64** in Airport for UTF-8 compatibility.

---

## Installation

```bash
pip install query-farm-duckdb-json-serialization
```

## API Usage

```python
from query_farm_duckdb_json_serialization.expression import Expression

column_names_by_index = ['first_name', 'last_name']
# If there are multiple expressions passed, these will all
# be logically joined with an AND operator.
#
# The DuckDB data typestypes of the columns bound by the expressions
# will be returned.
sql, bound_types = Expression.convert_to_sql(
    source=expressions,
    bound_column_names=column_names_by_index
)

```

- `expressions`: JSON-serialized list of DuckDB expression trees.
- `bound_column_names`: Column names indexed as expected by DuckDB.
- `sql`: Reconstructed `SQL WHERE` clause.
- `bound_types`: List of DuckDB data types for the bound columns.

## Input

The structure of DuckDB's serialized expressions may change between versions. Below is a working example.

```sql
CREATE TABLE test_type_int64 (v int64);
INSERT INTO test_type_int64 values (1234567890123456789);

-- This statement will generate the following JSON serialization.
SELECT v FROM test_type_int64 WHERE v = 1234567890123456789;
```

```json
[
  {
    "expression_class": "BOUND_COMPARISON",
    "type": "COMPARE_EQUAL",
    "alias": "",
    "query_location": 18446744073709551615,
    "left": {
      "expression_class": "BOUND_COLUMN_REF",
      "type": "BOUND_COLUMN_REF",
      "alias": "v",
      "query_location": 18446744073709551615,
      "return_type": {
        "id": "BIGINT",
        "type_info": null
      },
      "binding": {
        "table_index": 0,
        "column_index": 0
      },
      "depth": 0
    },
    "right": {
      "expression_class": "BOUND_CONSTANT",
      "type": "VALUE_CONSTANT",
      "alias": "",
      "query_location": 18446744073709551615,
      "value": {
        "type": {
          "id": "BIGINT",
          "type_info": null
        },
        "is_null": false,
        "value": 1234567890123456789
      }
    }
  }
]
```

## Author

This Python module was created by [Query.Farm](https://query.farm).

## License

MIT License. See [LICENSE](LICENSE) for details.
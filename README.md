# JsonSQL

JsonSQL is a Python class that allows safe execution of SQL queries from untrusted JSON input. It validates the input against allowed queries, tables, columns etc. before constructing a safe SQL string.

## Usage

### Installing the package

```python
pip install jsonsql
```

### Full SQL String

Import the JsonSQL class:

```python
from jsonsql import JsonSQL
```

Initialize it by passing allowed queries, items, tables, connections and column types:

```python
allowed_queries = ["SELECT"]
allowed_items = ["*"] 
allowed_tables = ["users"]
allowed_connections = ["WHERE"]
allowed_columns = {"id": int, "name": str}

jsonsql = JsonSQL(allowed_queries, allowed_items, allowed_tables, allowed_connections, allowed_columns)
```

Pass a JSON request to sql_parse() to validate and construct the SQL:

```python
request = {
  "query": "SELECT", 
  "items": ["*"],
  "table": "users",
  "connection": "WHERE",
  "logic": {
    "id": 123 
  }
}

sql, params = jsonsql.sql_parse(request)
```

The logic is validated against the allowed columns before constructing the final SQL string.

### Search Criteria for partial string

The logic_parse method can also be used independently to validate logic conditions without constructing a full SQL query. This allows reusing predefined or dynamically generated SQL strings while still validating any logic conditions passed from untrusted input.

For example:

```python
sql = "SELECT * FROM users WHERE"

logic = {
  "AND": [
     {"id": 123},
     {"name": "John"}
  ]
}

valid, message, params = jsonsql.logic_parse(logic)

if valid:
  full_sql = f"{sql} ({message})"
  # execute full_sql with params
```

This validates the logic while allowing the SQL query itself to be predefined or constructed separately.

The logic_parse method will return False if the input logic is invalid. Otherwise it returns the parsed logic string and any bound parameters for safe interpolation into a SQL query.

All arguments to JsonSQL like allowed_queries, allowed_columns etc. are optional and can be empty lists or dicts if full validation of the SQL syntax is not needed.

# JsonSQL

JsonSQL is a Python class that allows safe execution of SQL queries from untrusted JSON input. It validates the input against allowed queries, tables, columns etc. before constructing a safe SQL string.

## Usage

### Installing the package

```python
pip install git+https://github.com/weshinetech/JsonSQL.git
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

For JOIN support, you can also specify allowed JOIN types:

```python
jsonsql = JsonSQL(
    allowed_queries=["SELECT"],
    allowed_items=["*"],
    allowed_tables=["users", "roles", "user_roles"],
    allowed_connections=["WHERE"],
    allowed_columns={"id": int, "name": str, "role_id": int},
    allowed_joins=["INNER JOIN", "LEFT JOIN", "RIGHT JOIN"]
)
```

For more flexible permissions, you can use wildcards and blacklists:

```python
# Use ["*"] to allow all entities of a specific type
jsonsql = JsonSQL(
    allowed_queries=["*"],        # Allow any query type
    allowed_items=["*"],          # Allow any column/item
    allowed_tables=["*"],         # Allow any table
    allowed_connections=["*"],    # Allow any connection type
    allowed_columns={"*": object} # Allow any column with any type
)

# Use not_allowed_* parameters to explicitly forbid specific entities
jsonsql = JsonSQL(
    allowed_queries=["*"],
    allowed_items=["*"],
    allowed_tables=["*"],
    allowed_connections=["*"],
    allowed_columns={"*": object},
    allowed_joins=["*"],                                     # Allow all JOIN types
    not_allowed_tables=["app_secrets", "user_metadata"],     # Blacklist sensitive tables
    not_allowed_items=["password", "secret_key"],            # Blacklist sensitive columns
    not_allowed_queries=["DROP", "DELETE"],                  # Blacklist dangerous operations
    not_allowed_joins=["CROSS JOIN"]                         # Blacklist specific JOIN types
)

# Mix explicit permissions with wildcards and blacklists
jsonsql = JsonSQL(
    allowed_queries=["SELECT", "INSERT"],
    allowed_items=["name", "email", "age"],
    allowed_tables=["*"],                    # Allow all tables
    allowed_connections=["WHERE"],
    allowed_columns={"name": str, "email": str, "age": int},
    not_allowed_tables=["admin_users"],      # But not this table
    not_allowed_items=["password"]           # And not this item (overrides allowed_items)
)
```

Pass a JSON request to sql_parse() to validate and construct the SQL:

**Legacy Format (backward compatible):**

```python
request = {
  "query": "SELECT",
  "items": ["*"],
  "table": "users",
  "connection": "WHERE",
  "logic": {
    "id": {"=":123}
  }
}

valid, sql, params = jsonsql.sql_parse(request)
```

**Extended Format (with JOIN support):**

```python
request = {
  "query": "SELECT",
  "items": ["u.name", "r.role_name"],
  "from": {"table": "users", "alias": "u"},
  "joins": [
    {
      "type": "INNER JOIN",
      "table": "user_roles",
      "alias": "ur",
      "on": "u.id = ur.user_fk"
    },
    {
      "type": "INNER JOIN",
      "table": "roles",
      "alias": "r",
      "on": "ur.role_fk = r.id"
    }
  ],
  "where": {"u.id": {"=": 1}},
  "group_by": ["u.id"],
  "having": {"COUNT(*)": {">": 1}},
  "order_by": [{"column": "u.name", "direction": "ASC"}],
  "limit": 10,
  "offset": 0
}

valid, sql, params = jsonsql.sql_parse(request)
```

**SQL with actual values (direct execution):**

```python
# Generate SQL with placeholders (default - recommended for security)
valid, sql, params = jsonsql.sql_parse(request)

# Generate SQL with actual values substituted
valid, sql_with_values, params = jsonsql.sql_parse(request, with_values=True)
```

The logic is validated against the allowed columns before constructing the final SQL string.

The validation system follows this priority order:

1. **Blacklist Check**: If entity is in `not_allowed_*` list → **DENY** (highest priority)
2. **Strict Mode**: If `allowed_*` list is empty → **DENY** (secure by default)
3. **Wildcard Mode**: If `allowed_*` contains `"*"` → **ALLOW** (unless blacklisted)
4. **Explicit Allow**: If entity is in `allowed_*` list → **ALLOW**
5. **Default**: Otherwise → **DENY**

### JOIN Support

JsonSQL supports complex JOIN operations with the extended JSON format. Supported JOIN types include:

- `INNER JOIN`
- `LEFT JOIN` / `LEFT OUTER JOIN`
- `RIGHT JOIN` / `RIGHT OUTER JOIN`
- `FULL OUTER JOIN`
- `CROSS JOIN`
- `NATURAL JOIN`

**JOIN Configuration:**

```python
jsonsql = JsonSQL(
    allowed_queries=["SELECT"],
    allowed_items=["*"],
    allowed_tables=["users", "roles", "user_roles"],
    allowed_connections=["WHERE"],
    allowed_columns={"*": object},
    allowed_joins=["INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],  # Specify allowed JOIN types
    not_allowed_joins=["CROSS JOIN"]                          # Blacklist specific JOIN types
)
```

**JOIN Examples:**

```python
# Simple INNER JOIN
join_query = {
    "query": "SELECT",
    "items": ["u.name", "r.role_name"],
    "from": {"table": "users", "alias": "u"},
    "joins": [
        {
            "type": "INNER JOIN",
            "table": "user_roles",
            "alias": "ur",
            "on": "u.id = ur.user_fk"
        },
        {
            "type": "INNER JOIN",
            "table": "roles",
            "alias": "r",
            "on": "ur.role_fk = r.id"
        }
    ],
    "where": {"u.active": {"=": True}}
}

# Complex query with GROUP BY, HAVING, ORDER BY
complex_query = {
    "query": "SELECT",
    "items": ["r.role_name", "COUNT(u.id) as user_count"],
    "from": {"table": "roles", "alias": "r"},
    "joins": [
        {
            "type": "LEFT JOIN",
            "table": "user_roles",
            "alias": "ur",
            "on": "r.id = ur.role_fk"
        },
        {
            "type": "LEFT JOIN",
            "table": "users",
            "alias": "u",
            "on": "ur.user_fk = u.id"
        }
    ],
    "group_by": ["r.id", "r.role_name"],
    "having": {"COUNT(u.id)": {">": 0}},
    "order_by": [{"column": "user_count", "direction": "DESC"}],
    "limit": 10
}
```

### SQL Output Options

The `sql_parse()` method supports two output modes:

**1. Parameterized SQL (default - recommended for security):**

```python
valid, sql, params = jsonsql.sql_parse(request)
# Returns: "SELECT * FROM users WHERE id = ?" with params (123,)
# Usage: cursor.execute(sql, params)
```

**2. SQL with actual values (direct execution):**

```python
valid, sql_with_values, params = jsonsql.sql_parse(request, with_values=True)
# Returns: "SELECT * FROM users WHERE id = 123" with params ()
# Usage: cursor.execute(sql_with_values)
```

The `with_values=True` option substitutes all parameters directly into the SQL string, making it suitable for direct execution without parameter binding.

### Search Criteria for partial string

The logic_parse method can also be used independently to validate logic conditions without constructing a full SQL query. This allows reusing predefined or dynamically generated SQL strings while still validating any logic conditions passed from untrusted input.

For example:

```python
sql = "SELECT * FROM users WHERE"

logic = {
  "AND": [
     {"id": {"=":123}},
     {"name": {"=":"John"}}
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

### Current operations supported by the logic

Note: variables do mean columns in the way i am using them

**Basic Logic Operations:**

```json
{
  "AND":[],
  "OR":[],
  {"variable":{"<, >, =, etc":"value"}},
  {"variable":{"BETWEEN":["value1","value2"]}},
  {"variable":{"IN":["value1","value2","..."]}}
}
```

**Column Comparisons:**

```json
{ "variable": { "=": "othervariable" } }
```

**SQL Aggregations:**

```json
{ "variable": { "=": { "MIN": "variable" } } }
```

**Supported ORDER BY Directions:**

- `ASC` (ascending)
- `DESC` (descending)

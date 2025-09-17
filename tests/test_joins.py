"""
Comprehensive JOIN tests for JsonSQL using pytest.
"""

import os
import sys

import pytest

from jsonsql import JsonSQL

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def jsonsql_with_joins():
    """Fixture providing JsonSQL instance with JOIN support."""
    return JsonSQL(
        allowed_queries=["SELECT"],
        allowed_items=["*"],
        allowed_tables=["users", "roles", "user_roles",
                        "wst.users", "wst.roles", "wst.user_roles"],
        allowed_connections=["WHERE"],
        allowed_columns={"*": object},
        allowed_joins=["INNER JOIN", "LEFT JOIN",
                       "RIGHT JOIN", "FULL OUTER JOIN", "CROSS JOIN"]
    )


@pytest.fixture
def restricted_jsonsql():
    """Fixture providing restricted JsonSQL instance for security testing."""
    return JsonSQL(
        allowed_queries=["SELECT"],
        allowed_items=["*"],
        allowed_tables=["users", "roles"],
        allowed_joins=["INNER JOIN", "LEFT JOIN"]  # RIGHT JOIN not allowed
    )


class TestBasicJoins:
    """Test basic JOIN functionality."""

    def test_inner_join_basic(self, jsonsql_with_joins):
        """Test basic INNER JOIN functionality."""
        input_data = {
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
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id"
        assert params == ()

    def test_left_join_basic(self, jsonsql_with_joins):
        """Test basic LEFT JOIN functionality."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "LEFT JOIN",
                    "table": "user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                },
                {
                    "type": "LEFT JOIN",
                    "table": "roles",
                    "alias": "r",
                    "on": "ur.role_fk = r.id"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u LEFT JOIN user_roles AS ur ON u.id = ur.user_fk LEFT JOIN roles AS r ON ur.role_fk = r.id"
        assert params == ()

    def test_right_join_basic(self, jsonsql_with_joins):
        """Test basic RIGHT JOIN functionality."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "roles", "alias": "r"},
            "joins": [
                {
                    "type": "RIGHT JOIN",
                    "table": "user_roles",
                    "alias": "ur",
                    "on": "r.id = ur.role_fk"
                },
                {
                    "type": "RIGHT JOIN",
                    "table": "users",
                    "alias": "u",
                    "on": "ur.user_fk = u.id"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM roles AS r RIGHT JOIN user_roles AS ur ON r.id = ur.role_fk RIGHT JOIN users AS u ON ur.user_fk = u.id"
        assert params == ()

    def test_full_outer_join_basic(self, jsonsql_with_joins):
        """Test basic FULL OUTER JOIN functionality."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "FULL OUTER JOIN",
                    "table": "user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u FULL OUTER JOIN user_roles AS ur ON u.id = ur.user_fk"
        assert params == ()

    def test_cross_join_basic(self, jsonsql_with_joins):
        """Test basic CROSS JOIN functionality."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "CROSS JOIN",
                    "table": "roles",
                    "alias": "r"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u CROSS JOIN roles AS r"
        assert params == ()


class TestJoinWithClauses:
    """Test JOIN with various SQL clauses."""

    def test_join_with_where_clause(self, jsonsql_with_joins):
        """Test JOIN with WHERE clause."""
        input_data = {
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
            "where": {"u.id": {"=": 1}}
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id WHERE u.id = ?"
        assert params == (1,)

    def test_join_with_group_by_having(self, jsonsql_with_joins):
        """Test JOIN with GROUP BY and HAVING clauses."""
        input_data = {
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
            "having": {"COUNT(u.id)": {">": 0}}
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT r.role_name,COUNT(u.id) as user_count FROM roles AS r LEFT JOIN user_roles AS ur ON r.id = ur.role_fk LEFT JOIN users AS u ON ur.user_fk = u.id GROUP BY r.id,r.role_name HAVING COUNT(u.id) > ?"
        assert params == (0,)

    def test_join_with_order_by_limit(self, jsonsql_with_joins):
        """Test JOIN with ORDER BY and LIMIT clauses."""
        input_data = {
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
            "order_by": [{"column": "u.name", "direction": "ASC"}],
            "limit": 10
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id ORDER BY u.name ASC LIMIT 10"
        assert params == ()

    def test_join_with_offset(self, jsonsql_with_joins):
        """Test JOIN with LIMIT and OFFSET clauses."""
        input_data = {
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
            "limit": 10,
            "offset": 20
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id LIMIT 10 OFFSET 20"
        assert params == ()


class TestJoinVariations:
    """Test various JOIN variations and edge cases."""

    def test_join_without_alias(self, jsonsql_with_joins):
        """Test JOIN without table aliases."""
        input_data = {
            "query": "SELECT",
            "items": ["users.name", "roles.role_name"],
            "from": {"table": "users"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "user_roles",
                    "on": "users.id = user_roles.user_fk"
                },
                {
                    "type": "INNER JOIN",
                    "table": "roles",
                    "on": "user_roles.role_fk = roles.id"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT users.name,roles.role_name FROM users INNER JOIN user_roles ON users.id = user_roles.user_fk INNER JOIN roles ON user_roles.role_fk = roles.id"
        assert params == ()

    def test_join_with_schema_prefix(self, jsonsql_with_joins):
        """Test JOIN with schema-prefixed tables."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "wst.users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "wst.user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                },
                {
                    "type": "INNER JOIN",
                    "table": "wst.roles",
                    "alias": "r",
                    "on": "ur.role_fk = r.id"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM wst.users AS u INNER JOIN wst.user_roles AS ur ON u.id = ur.user_fk INNER JOIN wst.roles AS r ON ur.role_fk = r.id"
        assert params == ()

    def test_join_without_on_condition(self, jsonsql_with_joins):
        """Test JOIN without ON condition (CROSS JOIN)."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "CROSS JOIN",
                    "table": "roles",
                    "alias": "r"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u CROSS JOIN roles AS r"
        assert params == ()

    def test_join_with_complex_on_condition(self, jsonsql_with_joins):
        """Test JOIN with complex ON condition."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk AND u.status = 'active'"
                }
            ]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk AND u.status = 'active'"
        assert params == ()


class TestJoinSecurity:
    """Test JOIN security and validation."""

    def test_disallowed_join_type(self, restricted_jsonsql):
        """Test that disallowed JOIN types are rejected."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "RIGHT JOIN",  # This should be rejected
                    "table": "roles",
                    "alias": "r",
                    "on": "u.id = r.user_id"
                }
            ]
        }
        result, msg, params = restricted_jsonsql.sql_parse(input_data)
        assert result is False
        assert "JOIN type not allowed" in msg

    def test_disallowed_table_in_join(self, restricted_jsonsql):
        """Test that disallowed tables in JOINs are rejected."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "user_roles",  # This should be rejected
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                }
            ]
        }
        result, msg, params = restricted_jsonsql.sql_parse(input_data)
        assert result is False
        assert "Table not allowed" in msg

    def test_malicious_on_condition(self, jsonsql_with_joins):
        """Test that malicious ON conditions are rejected."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "roles",
                    "alias": "r",
                    "on": "u.id = r.user_id; DROP TABLE users; --"  # Malicious
                }
            ]
        }
        result, msg, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is False
        assert "Invalid JOIN condition" in msg

    def test_missing_from_clause(self, jsonsql_with_joins):
        """Test that missing FROM clause is handled properly."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "roles",
                    "alias": "r"
                }
            ]
        }
        result, msg, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is False
        assert "Missing FROM clause" in msg

    def test_invalid_join_structure(self, jsonsql_with_joins):
        """Test that invalid JOIN structure is handled properly."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    # Missing table field
                    "alias": "r",
                    "on": "u.id = r.user_id"
                }
            ]
        }
        result, msg, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is False
        assert "Error parsing SQL" in msg


class TestBackwardCompatibility:
    """Test backward compatibility with legacy format."""

    def test_legacy_format_still_works(self, jsonsql_with_joins):
        """Test that legacy format still works with JOIN support enabled."""
        input_data = {
            "query": "SELECT",
            "items": ["*"],
            "table": "users",
            "connection": "WHERE",
            "logic": {"id": {"=": 1}}
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT * FROM users WHERE id = ?"
        assert params == (1,)

    def test_mixed_legacy_and_new_format(self, jsonsql_with_joins):
        """Test mixing legacy table with new WHERE format."""
        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "table": "users",  # Legacy table format
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "user_roles",
                    "alias": "ur",
                    "on": "users.id = ur.user_fk"
                }
            ],
            "where": {"users.id": {"=": 1}}  # New WHERE format
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.name,r.role_name FROM users INNER JOIN user_roles AS ur ON users.id = ur.user_fk WHERE users.id = ?"
        assert params == (1,)


class TestRealWorldScenarios:
    """Test real-world JOIN scenarios."""

    def test_user_role_many_to_many(self, jsonsql_with_joins):
        """Test many-to-many relationship between users and roles."""
        input_data = {
            "query": "SELECT",
            "items": ["u.id", "u.name", "u.email", "r.role_name"],
            "from": {"table": "wst.users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "wst.user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                },
                {
                    "type": "INNER JOIN",
                    "table": "wst.roles",
                    "alias": "r",
                    "on": "ur.role_fk = r.id"
                }
            ],
            "where": {"u.id": {"=": 1}},
            "order_by": [{"column": "r.role_name", "direction": "ASC"}]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.id,u.name,u.email,r.role_name FROM wst.users AS u INNER JOIN wst.user_roles AS ur ON u.id = ur.user_fk INNER JOIN wst.roles AS r ON ur.role_fk = r.id WHERE u.id = ? ORDER BY r.role_name ASC"
        assert params == (1,)

    def test_role_statistics(self, jsonsql_with_joins):
        """Test role statistics with aggregation."""
        input_data = {
            "query": "SELECT",
            "items": ["r.role_name", "COUNT(DISTINCT u.id) as user_count"],
            "from": {"table": "wst.roles", "alias": "r"},
            "joins": [
                {
                    "type": "LEFT JOIN",
                    "table": "wst.user_roles",
                    "alias": "ur",
                    "on": "r.id = ur.role_fk"
                },
                {
                    "type": "LEFT JOIN",
                    "table": "wst.users",
                    "alias": "u",
                    "on": "ur.user_fk = u.id"
                }
            ],
            "group_by": ["r.id", "r.role_name"],
            "having": {"COUNT(DISTINCT u.id)": {">": 0}},
            "order_by": [{"column": "user_count", "direction": "DESC"}]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT r.role_name,COUNT(DISTINCT u.id) as user_count FROM wst.roles AS r LEFT JOIN wst.user_roles AS ur ON r.id = ur.role_fk LEFT JOIN wst.users AS u ON ur.user_fk = u.id GROUP BY r.id,r.role_name HAVING COUNT(DISTINCT u.id) > ? ORDER BY user_count DESC"
        assert params == (0,)

    def test_users_without_roles(self, jsonsql_with_joins):
        """Test finding users without any roles."""
        input_data = {
            "query": "SELECT",
            "items": ["u.id", "u.name", "u.email"],
            "from": {"table": "wst.users", "alias": "u"},
            "joins": [
                {
                    "type": "LEFT JOIN",
                    "table": "wst.user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                }
            ],
            "where": {"ur.user_fk": {"=": None}},
            "order_by": [{"column": "u.name", "direction": "ASC"}]
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.id,u.name,u.email FROM wst.users AS u LEFT JOIN wst.user_roles AS ur ON u.id = ur.user_fk WHERE ur.user_fk = ? ORDER BY u.name ASC"
        assert params == (None,)

    def test_multi_role_users(self, jsonsql_with_joins):
        """Test finding users with multiple roles."""
        input_data = {
            "query": "SELECT",
            "items": ["u.id", "u.name", "u.email", "COUNT(ur.role_fk) as role_count"],
            "from": {"table": "wst.users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "wst.user_roles",
                    "alias": "ur",
                    "on": "u.id = ur.user_fk"
                }
            ],
            "group_by": ["u.id", "u.name", "u.email"],
            "having": {"COUNT(ur.role_fk)": {">": 1}},
            "order_by": [{"column": "role_count", "direction": "DESC"}],
            "limit": 10
        }
        result, sql, params = jsonsql_with_joins.sql_parse(input_data)
        assert result is True
        assert sql == "SELECT u.id,u.name,u.email,COUNT(ur.role_fk) as role_count FROM wst.users AS u INNER JOIN wst.user_roles AS ur ON u.id = ur.user_fk GROUP BY u.id,u.name,u.email HAVING COUNT(ur.role_fk) > ? ORDER BY role_count DESC LIMIT 10"
        assert params == (1,)


class TestSQLWithValues:
    """Test SQL generation with actual values instead of placeholders."""

    def test_sql_with_values_basic(self, jsonsql_with_joins):
        """Test basic SQL with values generation."""
        input_data = {
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
            "where": {"u.id": {"=": 1}}
        }
        result, sql_with_values, params = jsonsql_with_joins.sql_parse(
            input_data, with_values=True)
        assert result is True
        assert sql_with_values == "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id WHERE u.id = 1"
        assert "?" not in sql_with_values  # No placeholders should remain

    def test_sql_with_values_string_escaping(self, jsonsql_with_joins):
        """Test SQL with values handles string escaping correctly."""
        input_data = {
            "query": "SELECT",
            "items": ["*"],
            "table": "users",
            "connection": "WHERE",
            "logic": {"name": {"=": "O'Connor"}}  # String with single quote
        }
        result, sql_with_values, params = jsonsql_with_joins.sql_parse(
            input_data, with_values=True)
        assert result is True
        assert sql_with_values == "SELECT * FROM users WHERE name = 'O''Connor'"
        assert "?" not in sql_with_values

    def test_sql_with_values_null_handling(self, jsonsql_with_joins):
        """Test SQL with values handles NULL values correctly."""
        input_data = {
            "query": "SELECT",
            "items": ["*"],
            "table": "users",
            "connection": "WHERE",
            "logic": {"deleted_at": {"=": None}}
        }
        result, sql_with_values, params = jsonsql_with_joins.sql_parse(
            input_data, with_values=True)
        assert result is True
        assert sql_with_values == "SELECT * FROM users WHERE deleted_at = NULL"
        assert "?" not in sql_with_values

    def test_sql_with_values_error_handling(self, jsonsql_with_joins):
        """Test SQL with values handles errors correctly."""
        input_data = {
            "query": "SELECT",
            "items": ["*"],
            "joins": [
                {
                    "type": "INVALID JOIN",  # This should cause an error
                    "table": "roles"
                }
            ]
        }
        result, error_msg, params = jsonsql_with_joins.sql_parse(
            input_data, with_values=True)
        assert result is False
        assert "Missing FROM clause" in error_msg or "Error" in error_msg

    def test_sql_with_values_no_parameters(self, jsonsql_with_joins):
        """Test SQL with values when there are no parameters."""
        input_data = {
            "query": "SELECT",
            "items": ["*"],
            "table": "users"
        }
        result, sql_with_values, params = jsonsql_with_joins.sql_parse(
            input_data, with_values=True)
        assert result is True
        assert sql_with_values == "SELECT * FROM users"
        assert "?" not in sql_with_values

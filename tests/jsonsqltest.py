import unittest

from jsonsql import JsonSQL


class TestLogicParse(unittest.TestCase):

    def test_invalid_input(self):
        jsonsql = JsonSQL([], [], [], [], {})
        input = {'invalid': 'value'}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Invalid Input - invalid")

    def test_bad_and_non_list(self):
        jsonsql = JsonSQL([], [], [], [], {})
        input = {'AND': 'value'}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Bad AND, non list")

    def test_bad_column_type(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str})
        input = {'col1': {"=": 123}}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Bad col1, non <class 'str'>")

    def test_valid_single_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str})
        input = {'col1': {"=": 'value'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 = ?")
        self.assertEqual(params, ('value',))

    def test_invalid_boolean_len(self):
        jsonsql = JsonSQL([], [], [], [], {})
        input = {'AND': ['cond']}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Invalid boolean length, must be >= 2")

    def test_valid_multi_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str, 'col2': str})
        input = {'AND': [{'col1': {"=": 'value1'}}, {'col2': {"=": 'value2'}}]}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "(col1 = ? AND col2 = ?)")
        self.assertEqual(params, ('value1', 'value2'))

    def test_valid_gt_comparison_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'>': 10}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 > ?")
        self.assertEqual(params, (10,))

    def test_valid_lt_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'<': 10}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 < ?")
        self.assertEqual(params, (10,))

    def test_valid_gte_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'>=': 10}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 >= ?")
        self.assertEqual(params, (10,))

    def test_valid_lte_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'<=': 10}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 <= ?")
        self.assertEqual(params, (10,))

    def test_valid_neq_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'!=': 10}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 <> ?")
        self.assertEqual(params, (10,))

    def test_invalid_operator(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'!': 10}}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Non Valid comparitor - !")

    def test_valid_between_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'BETWEEN': [5, 10]}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 BETWEEN ? AND ?")
        self.assertEqual(params, (5, 10))

    def test_valid_in_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int})
        input = {'col1': {'IN': [5, 10, 15]}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 IN (?,?,?)")
        self.assertEqual(params, (5, 10, 15))

    def test_valid_eq_condition_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int, 'col2': int})
        input = {'col1': {'=': 'col2'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 = col2")
        self.assertEqual(params, ())

    def test_valid_gt_condition_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int, 'col2': int})
        input = {'col1': {'>': 'col2'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 > col2")
        self.assertEqual(params, ())

    def test_valid_lt_condition_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int, 'col2': int})
        input = {'col1': {'<': 'col2'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 < col2")
        self.assertEqual(params, ())

    def test_valid_gte_condition_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int, 'col2': int})
        input = {'col1': {'>=': 'col2'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 >= col2")
        self.assertEqual(params, ())

    def test_valid_lte_condition_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int, 'col2': int})
        input = {'col1': {'<=': 'col2'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 <= col2")
        self.assertEqual(params, ())

    def test_valid_neq_condition_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': int, 'col2': int})
        input = {'col1': {'!=': 'col2'}}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 <> col2")
        self.assertEqual(params, ())


class TestSQLParse(unittest.TestCase):

    def test_missing_argument(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': ['*'], "connection": "WHERE"}
        result, msg, params = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Missing argument table")

    def test_bad_query(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'INSERT', 'items': [
            '*'], 'table': 'table1', 'connection': 'WHERE'}
        result, msg, params = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Query not allowed - INSERT")

    def test_bad_item(self):
        jsonsql = JsonSQL(['SELECT'], ['good'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': [
            'bad'], 'table': 'table1', 'connection': 'WHERE'}
        result, msg, params = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Item not allowed - bad")

    def test_bad_table(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': [
            '*'], 'table': 'bad', 'connection': 'WHERE'}
        result, msg, params = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Table not allowed - bad")

    def test_valid_sql_no_logic(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], [], {})
        input = {'query': 'SELECT', 'items': ['*'], 'table': 'table1'}
        result, sql, params = jsonsql.sql_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "SELECT * FROM table1")
        self.assertEqual(params, ())

    def test_valid_sql_with_logic(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'],
                          ['WHERE'], {"col1": int})
        input = {'query': 'SELECT', 'items': [
            '*'], 'table': 'table1', 'connection': 'WHERE', 'logic': {'col1': {'<=': 2}}}
        result, sql, params = jsonsql.sql_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "SELECT * FROM table1 WHERE col1 <= ?")
        self.assertEqual(params, (2,))

    def test_valid_sql_without_logic_with_aggregate_table(self):
        jsonsql = JsonSQL(['SELECT'], ['column'], ['table1'], [], {})
        input = {'query': 'SELECT', 'items': [
            {"MIN": 'column'}], 'table': "table1"}
        result, sql, params = jsonsql.sql_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "SELECT MIN(column) FROM table1")
        self.assertEqual(params, ())


class TestJoinSupport(unittest.TestCase):
    """Test JOIN functionality in JsonSQL."""

    def setUp(self):
        """Set up test fixtures with JOIN support."""
        self.jsonsql = JsonSQL(
            allowed_queries=["SELECT"],
            allowed_items=["*"],
            allowed_tables=["users", "roles", "user_roles",
                            "wst.users", "wst.roles", "wst.user_roles"],
            allowed_connections=["WHERE"],
            allowed_columns={"*": object},
            allowed_joins=["INNER JOIN", "LEFT JOIN",
                           "RIGHT JOIN", "FULL OUTER JOIN", "CROSS JOIN"]
        )

    def test_inner_join_basic(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id")
        self.assertEqual(params, ())

    def test_left_join_basic(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u LEFT JOIN user_roles AS ur ON u.id = ur.user_fk LEFT JOIN roles AS r ON ur.role_fk = r.id")
        self.assertEqual(params, ())

    def test_right_join_basic(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM roles AS r RIGHT JOIN user_roles AS ur ON r.id = ur.role_fk RIGHT JOIN users AS u ON ur.user_fk = u.id")
        self.assertEqual(params, ())

    def test_full_outer_join_basic(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u FULL OUTER JOIN user_roles AS ur ON u.id = ur.user_fk")
        self.assertEqual(params, ())

    def test_cross_join_basic(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u CROSS JOIN roles AS r")
        self.assertEqual(params, ())

    def test_join_with_where_clause(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id WHERE u.id = ?")
        self.assertEqual(params, (1,))

    def test_join_with_group_by_having(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(sql, "SELECT r.role_name,COUNT(u.id) as user_count FROM roles AS r LEFT JOIN user_roles AS ur ON r.id = ur.role_fk LEFT JOIN users AS u ON ur.user_fk = u.id GROUP BY r.id,r.role_name HAVING COUNT(u.id) > ?")
        self.assertEqual(params, (0,))

    def test_join_with_order_by_limit(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id ORDER BY u.name ASC LIMIT 10")
        self.assertEqual(params, ())

    def test_join_with_offset(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk INNER JOIN roles AS r ON ur.role_fk = r.id LIMIT 10 OFFSET 20")
        self.assertEqual(params, ())

    def test_join_without_alias(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT users.name,roles.role_name FROM users INNER JOIN user_roles ON users.id = user_roles.user_fk INNER JOIN roles ON user_roles.role_fk = roles.id")
        self.assertEqual(params, ())

    def test_join_with_schema_prefix(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM wst.users AS u INNER JOIN wst.user_roles AS ur ON u.id = ur.user_fk INNER JOIN wst.roles AS r ON ur.role_fk = r.id")
        self.assertEqual(params, ())

    def test_join_without_on_condition(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u CROSS JOIN roles AS r")
        self.assertEqual(params, ())

    def test_join_with_complex_on_condition(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users AS u INNER JOIN user_roles AS ur ON u.id = ur.user_fk AND u.status = 'active'")
        self.assertEqual(params, ())

    def test_join_validation_disallowed_join_type(self):
        """Test that disallowed JOIN types are rejected."""
        restricted_jsonsql = JsonSQL(
            allowed_queries=["SELECT"],
            allowed_items=["*"],
            allowed_tables=["users", "roles"],
            allowed_joins=["INNER JOIN", "LEFT JOIN"]  # RIGHT JOIN not allowed
        )

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
        self.assertFalse(result)
        self.assertIn("JOIN type not allowed", msg)

    def test_join_validation_disallowed_table(self):
        """Test that disallowed tables in JOINs are rejected."""
        restricted_jsonsql = JsonSQL(
            allowed_queries=["SELECT"],
            allowed_items=["*"],
            allowed_tables=["users"],  # roles not allowed
            allowed_joins=["INNER JOIN"]
        )

        input_data = {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "roles",  # This should be rejected
                    "alias": "r",
                    "on": "u.id = r.user_id"
                }
            ]
        }
        result, msg, params = restricted_jsonsql.sql_parse(input_data)
        self.assertFalse(result)
        self.assertIn("Table not allowed", msg)

    def test_join_validation_malicious_on_condition(self):
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
        result, msg, params = self.jsonsql.sql_parse(input_data)
        self.assertFalse(result)
        self.assertIn("Invalid JOIN condition", msg)

    def test_join_validation_missing_from_clause(self):
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
        result, msg, params = self.jsonsql.sql_parse(input_data)
        self.assertFalse(result)
        self.assertIn("Missing FROM clause", msg)

    def test_join_validation_invalid_join_structure(self):
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
        result, msg, params = self.jsonsql.sql_parse(input_data)
        self.assertFalse(result)
        self.assertIn("Error parsing SQL", msg)

    def test_legacy_format_still_works(self):
        """Test that legacy format still works with JOIN support enabled."""
        input_data = {
            "query": "SELECT",
            "items": ["*"],
            "table": "users",
            "connection": "WHERE",
            "logic": {"id": {"=": 1}}
        }
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(sql, "SELECT * FROM users WHERE id = ?")
        self.assertEqual(params, (1,))

    def test_mixed_legacy_and_new_format(self):
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
        result, sql, params = self.jsonsql.sql_parse(input_data)
        self.assertTrue(result)
        self.assertEqual(
            sql, "SELECT u.name,r.role_name FROM users INNER JOIN user_roles AS ur ON users.id = ur.user_fk WHERE users.id = ?")
        self.assertEqual(params, (1,))


if __name__ == "__main__":
    unittest.main()

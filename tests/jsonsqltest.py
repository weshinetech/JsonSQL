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
        input = {'col1': {"=":123}}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Bad col1, non <class 'str'>")

    def test_valid_single_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str})
        input = {'col1': {"=":'value'}}
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
        input = {'AND': [{'col1': {"=":'value1'}}, {'col2': {"=":'value2'}}]}
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
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Missing argument table")

    def test_bad_query(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'INSERT', 'items': [
            '*'], 'table': 'table1', 'connection': 'WHERE'}
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Query not allowed - INSERT")

    def test_bad_item(self):
        jsonsql = JsonSQL(['SELECT'], ['good'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': [
            'bad'], 'table': 'table1', 'connection': 'WHERE'}
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Item not allowed - bad")

    def test_bad_table(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': [
            '*'], 'table': 'bad', 'connection': 'WHERE'}
        result, msg = jsonsql.sql_parse(input)
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
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {"col1":int})
        input = {'query': 'SELECT', 'items': ['*'], 'table': 'table1', 'connection': 'WHERE', 'logic': {'col1': {'<=': 2}}}
        result, sql, params = jsonsql.sql_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "SELECT * FROM table1 WHERE col1 <= ?")
        self.assertEqual(params, (2,))


if __name__ == "__main__":
    unittest.main()
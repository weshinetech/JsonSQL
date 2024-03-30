import pytest
from jsonsql import JsonSQL


## Test Logic Parse


@pytest.fixture
def jsonsql() -> JsonSQL:
    return JsonSQL([], [], [], [], {})


def test_invalid_input(jsonsql: JsonSQL):
    input = {"invalid": "value"}
    result, msg = jsonsql.logic_parse(input)
    assert result is False
    assert msg == "Invalid Input - invalid"


def test_bad_and_non_list(jsonsql: JsonSQL):
    input = {"AND": "value"}
    result, msg = jsonsql.logic_parse(input)
    assert result is False
    assert msg == "Bad AND, non list"


def test_bad_column_type(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": str}
    input = {"col1": {"=": 123}}
    result, msg = jsonsql.logic_parse(input)
    assert result is False
    assert msg == "Bad col1, non <class 'str'>"


def test_valid_single_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": str}
    input = {"col1": {"=": "value"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 = ?"
    assert params == ("value",)


def test_invalid_boolean_len(jsonsql: JsonSQL):
    input = {"AND": ["cond"]}
    result, msg = jsonsql.logic_parse(input)
    assert result is False
    assert msg == "Invalid boolean length, must be >= 2"


def test_valid_multi_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": str, "col2": str}
    input = {"AND": [{"col1": {"=": "value1"}}, {"col2": {"=": "value2"}}]}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "(col1 = ? AND col2 = ?)"
    assert params == ("value1", "value2")


def test_valid_gt_comparison_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {">": 10}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 > ?"
    assert params == (10,)


def test_valid_lt_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {"<": 10}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 < ?"
    assert params == (10,)


def test_valid_gte_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {">=": 10}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 >= ?"
    assert params == (10,)


def test_valid_lte_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {"<=": 10}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 <= ?"
    assert params == (10,)


def test_valid_neq_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {"!=": 10}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 <> ?"
    assert params == (10,)


def test_invalid_operator(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {"!": 10}}
    result, msg = jsonsql.logic_parse(input)
    assert result is False
    assert msg == "Non Valid comparitor - !"


def test_valid_between_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {"BETWEEN": [5, 10]}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 BETWEEN ? AND ?"
    assert params == (5, 10)


def test_valid_in_condition(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {"col1": {"IN": [5, 10, 15]}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 IN (?,?,?)"
    assert params == (5, 10, 15)


def test_valid_eq_condition_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int, "col2": int}
    input = {"col1": {"=": "col2"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 = col2"
    assert params == ()


def test_valid_gt_condition_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int, "col2": int}
    input = {"col1": {">": "col2"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 > col2"
    assert params == ()


def test_valid_lt_condition_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int, "col2": int}
    input = {"col1": {"<": "col2"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 < col2"
    assert params == ()


def test_valid_gte_condition_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int, "col2": int}
    input = {"col1": {">=": "col2"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 >= col2"
    assert params == ()


def test_valid_lte_condition_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int, "col2": int}
    input = {"col1": {"<=": "col2"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 <= col2"
    assert params == ()


def test_valid_neq_condition_column(jsonsql: JsonSQL):
    jsonsql.ALLOWED_COLUMNS = {"col1": int, "col2": int}
    input = {"col1": {"!=": "col2"}}
    result, sql, params = jsonsql.logic_parse(input)
    assert result is True
    assert sql == "col1 <> col2"
    assert params == ()


## Test SQL Parse


def test_missing_argument(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["*"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    jsonsql.ALLOWED_CONNECTIONS = ["WHERE"]
    input = {"query": "SELECT", "items": ["*"], "connection": "WHERE"}
    result, msg = jsonsql.sql_parse(input)
    assert result is False
    assert msg == "Missing argument table"


def test_bad_query(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["*"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    jsonsql.ALLOWED_CONNECTIONS = ["WHERE"]
    input = {
        "query": "INSERT",
        "items": ["*"],
        "table": "table1",
        "connection": "WHERE",
    }
    result, msg = jsonsql.sql_parse(input)
    assert result is False
    assert msg == "Query not allowed - INSERT"


def test_bad_item(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["good"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    jsonsql.ALLOWED_CONNECTIONS = ["WHERE"]
    input = {
        "query": "SELECT",
        "items": ["bad"],
        "table": "table1",
        "connection": "WHERE",
    }
    result, msg = jsonsql.sql_parse(input)
    assert result is False
    assert msg == "Item not allowed - bad"


def test_bad_table(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["*"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    jsonsql.ALLOWED_CONNECTIONS = ["WHERE"]
    input = {"query": "SELECT", "items": ["*"], "table": "bad", "connection": "WHERE"}
    result, msg = jsonsql.sql_parse(input)
    assert result is False
    assert msg == "Table not allowed - bad"


def test_valid_sql_no_logic(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["*"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    input = {"query": "SELECT", "items": ["*"], "table": "table1"}
    result, sql, params = jsonsql.sql_parse(input)
    assert result is True
    assert sql == "SELECT * FROM table1"
    assert params == ()


def test_valid_sql_with_logic(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["*"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    jsonsql.ALLOWED_CONNECTIONS = ["WHERE"]
    jsonsql.ALLOWED_COLUMNS = {"col1": int}
    input = {
        "query": "SELECT",
        "items": ["*"],
        "table": "table1",
        "connection": "WHERE",
        "logic": {"col1": {"<=": 2}},
    }
    result, sql, params = jsonsql.sql_parse(input)
    assert result is True
    assert sql == "SELECT * FROM table1 WHERE col1 <= ?"
    assert params == (2,)


def test_valid_sql_without_logic_with_aggregate_table(jsonsql: JsonSQL):
    jsonsql.ALLOWED_QUERIES = ["SELECT"]
    jsonsql.ALLOWED_ITEMS = ["column"]
    jsonsql.ALLOWED_TABLES = ["table1"]
    input = {"query": "SELECT", "items": [{"MIN": "column"}], "table": "table1"}
    result, sql, params = jsonsql.sql_parse(input)
    assert result is True
    assert sql == "SELECT MIN(column) FROM table1"
    assert params == ()

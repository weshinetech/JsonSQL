import re
from typing import Any, Dict, List, Literal, Union


class JsonSQL:
    def __init__(
        self,
        allowed_queries: List[str] = None,
        allowed_items: List[str] = None,
        allowed_tables: List[str] = None,
        allowed_connections: List[str] = None,
        allowed_columns: Dict[str, type] = None,
        allowed_joins: List[str] = None,
        not_allowed_queries: List[str] = None,
        not_allowed_items: List[str] = None,
        not_allowed_tables: List[str] = None,
        not_allowed_connections: List[str] = None,
        not_allowed_columns: List[str] = None,
        not_allowed_joins: List[str] = None
    ):
        """Initializes JsonSQL instance with allowed/not_allowed queries, items,
        tables, connections, columns, and joins.

        Args:
            allowed_queries (List[str], optional): Allowed SQL query strings.
                Use ["*"] to allow all. Defaults to [] (strict mode).
            allowed_items (List[str], optional): Allowed SQL SELECT fields.
                Use ["*"] to allow all. Defaults to [] (strict mode).
            allowed_tables (List[str], optional): Allowed SQL FROM tables.
                Use ["*"] to allow all. Defaults to [] (strict mode).
            allowed_connections (List[str], optional): Allowed SQL WHERE conditions.
                Use ["*"] to allow all. Defaults to [] (strict mode).
            allowed_columns (Dict[str, type], optional): Allowed columns per table.
                Use {"*": object} to allow all. Defaults to {} (strict mode).
            allowed_joins (List[str], optional): Allowed JOIN types.
                Use ["*"] to allow all. Defaults to ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"].
            not_allowed_queries (List[str], optional): Explicitly forbidden queries.
                Takes precedence over allowed_queries. Defaults to [].
            not_allowed_items (List[str], optional): Explicitly forbidden items.
                Takes precedence over allowed_items. Defaults to [].
            not_allowed_tables (List[str], optional): Explicitly forbidden tables.
                Takes precedence over allowed_tables. Defaults to [].
            not_allowed_connections (List[str], optional): Explicitly forbidden connections.
                Takes precedence over allowed_connections. Defaults to [].
            not_allowed_columns (List[str], optional): Explicitly forbidden columns.
                Takes precedence over allowed_columns. Defaults to [].
            not_allowed_joins (List[str], optional): Explicitly forbidden JOIN types.
                Takes precedence over allowed_joins. Defaults to [].
        """
        # Initialize allowed lists with default empty lists for strict mode
        self.ALLOWED_QUERIES = allowed_queries if allowed_queries is not None else []
        self.ALLOWED_ITEMS = allowed_items if allowed_items is not None else []
        self.ALLOWED_CONNECTIONS = allowed_connections if allowed_connections is not None else []
        self.ALLOWED_COLUMNS = allowed_columns if allowed_columns is not None else {}

        # Initialize JOIN support
        self.ALLOWED_JOINS = allowed_joins if allowed_joins is not None else [
            "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN",
            "CROSS JOIN", "NATURAL JOIN"
        ]

        # Initialize not_allowed lists
        self.NOT_ALLOWED_QUERIES = not_allowed_queries if not_allowed_queries is not None else []
        self.NOT_ALLOWED_ITEMS = not_allowed_items if not_allowed_items is not None else []
        self.NOT_ALLOWED_TABLES = not_allowed_tables if not_allowed_tables is not None else []
        self.NOT_ALLOWED_CONNECTIONS = not_allowed_connections if not_allowed_connections is not None else []
        self.NOT_ALLOWED_COLUMNS = not_allowed_columns if not_allowed_columns is not None else []
        self.NOT_ALLOWED_JOINS = not_allowed_joins if not_allowed_joins is not None else []

        # Enhanced table handling from dev branch
        allowed_tables = allowed_tables if allowed_tables is not None else []
        table_dict = {}
        for table in allowed_tables:
            if isinstance(table, dict) and isinstance(table[list(table)[0]], list):
                table_dict[list(table)[0]] = table[list(table)[0]]
            elif isinstance(table, dict) and not isinstance(
                table[list(table)[0]], list
            ):
                raise TypeError(f"Table {table} items must be a list")
            elif isinstance(table, str):
                table_dict[table] = [None]
            else:
                raise TypeError(f"{table} not str or dict")

        self.ALLOWED_TABLES = table_dict

        self.LOGICAL = ("AND", "OR")
        self.COMPARISON = ("=", ">", "<", ">=", "<=", "<>", "!=")
        self.SPECIAL_COMPARISON = ("BETWEEN", "IN")
        self.AGGREGATES = ("MIN", "MAX", "SUM", "AVG", "COUNT")

    def _is_entity_allowed(
        self,
        entity: str,
        allowed_list: List[str],
        not_allowed_list: List[str]
    ) -> bool:
        """Check if an entity is allowed based on whitelist and blacklist rules.

        Validation logic:
        1. If entity is in not_allowed_list → DENY (blacklist takes precedence)
        2. If allowed_list is empty → DENY (strict mode)
        3. If allowed_list contains "*" → ALLOW (wildcard mode)
        4. If entity is in allowed_list → ALLOW
        5. Otherwise → DENY

        Args:
            entity (str): The entity to validate (e.g., table name, query type).
            allowed_list (List[str]): List of allowed entities or ["*"] for wildcard.
            not_allowed_list (List[str]): List of explicitly forbidden entities.

        Returns:
            bool: True if entity is allowed, False otherwise.
        """
        # Check blacklist first (takes precedence)
        if entity in not_allowed_list:
            return False

        # Strict mode: empty allowed list means nothing is allowed
        if not allowed_list:
            return False

        # Wildcard mode: "*" allows everything (except blacklisted)
        if "*" in allowed_list:
            return True

        # Explicit whitelist check
        return entity in allowed_list

    def _is_table_allowed(self, table: str) -> bool:
        """Check if a table is allowed, handling both simple and enhanced table format."""
        # Check blacklist first
        if table in self.NOT_ALLOWED_TABLES:
            return False

        # Handle wildcard tables from our enhancement
        if hasattr(self, 'NOT_ALLOWED_TABLES') and len(self.ALLOWED_QUERIES) > 0:
            # We're using our enhanced system
            allowed_table_names = [k for k in self.ALLOWED_TABLES.keys()]
            return self._is_entity_allowed(table, allowed_table_names, self.NOT_ALLOWED_TABLES)
        else:
            # Original dev branch logic
            return table in self.ALLOWED_TABLES

    def _is_column_allowed(self, column: str) -> bool:
        """Check if a column is allowed based on column-specific rules.

        Args:
            column (str): The column name to validate.

        Returns:
            bool: True if column is allowed, False otherwise.
        """
        # Check blacklist first
        if column in self.NOT_ALLOWED_COLUMNS:
            return False

        # Strict mode: empty allowed columns means nothing is allowed
        if not self.ALLOWED_COLUMNS:
            return False

        # Wildcard mode: "*" key allows all columns
        if "*" in self.ALLOWED_COLUMNS:
            return True

        # Explicit column check
        return column in self.ALLOWED_COLUMNS

    def make_aggregate(self, aggregate: dict, param: bool = False) -> tuple[str, any]:
        """Enhanced aggregate function from dev branch."""
        # Extract the aggregate function name and its argument
        aggregate_function = list(aggregate)[0]
        aggregate_argument = aggregate[aggregate_function]

        # Construct the SQL aggregate function string
        aggregate_string = (
            f"{aggregate_function}({aggregate_argument if not param else '?'})"
        )

        # Return the aggregate string and its argument
        return aggregate_string, aggregate_argument

    def is_another_column(self, value: str) -> bool:
        """Check if a value represents another column name.

        This method determines if a value should be treated as a column reference
        rather than a literal value. With wildcard columns, we need to be more
        careful to avoid treating all strings as column references.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if value is an allowed column name, False otherwise.
        """
        try:
            # If we don't have wildcard columns, use the original logic
            if "*" not in self.ALLOWED_COLUMNS:
                return self._is_column_allowed(value)

            # With wildcard columns, only treat as column if explicitly listed
            # or if it's not blacklisted and looks like a column name
            if value in self.NOT_ALLOWED_COLUMNS:
                return False

            # If we have explicit columns defined alongside wildcard, check those first
            explicit_columns = {k: v for k,
                                v in self.ALLOWED_COLUMNS.items() if k != "*"}
            if explicit_columns and value in explicit_columns:
                return True

            # For wildcard mode, we're more conservative - only treat as column
            # if it doesn't look like a typical literal value
            # This is a heuristic: values that are purely numeric, contain spaces,
            # or are common literal patterns are treated as literals
            if (value.isdigit() or
                ' ' in value or
                value.lower() in ['true', 'false', 'null'] or
                (value.startswith('"') and value.endswith('"')) or
                    (value.startswith("'") and value.endswith("'"))):
                return False

            # If we reach here with wildcard columns, treat as potential column
            return True

        except (TypeError, AttributeError):
            return False

    def is_valid_aggregate(self, aggregate: dict) -> bool:
        if not isinstance(aggregate, dict):
            return False

        operation = list(aggregate)[0]
        value = aggregate[operation]
        if operation not in self.AGGREGATES:
            return False

        return self.is_another_column(value)

    def is_valid_value(self, value: any, valuetype: any) -> bool:
        # Check if the value is an aggregate
        if isinstance(value, dict):
            return self.is_valid_aggregate(value)

        # Check if the value is another column
        if not isinstance(value, list) and self.is_another_column(value):
            return True

        # Check if the value is of the expected type
        return isinstance(value, valuetype)

    def is_special_comparison(
        self, comparator: str, value: any, valuetype: any
    ) -> bool:
        """Checks if a comparator and value match the special comparison operators.

        Special comparison operators include BETWEEN and IN. This checks if the
        comparator is one of those, and if the value matches the expected format.

        Args:
            comparator (str): The comparison operator.
            value: The comparison value.
            valuetype: The expected type of the comparison value.

        Returns:
            bool: True if it is a valid special comparison, False otherwise.
        """
        def all_values_allowed(value, valuetype):
            """Checks if all values in a list are of the specified type.

            Args:
                value (list): The list of values to check.
                valuetype: The expected type of each value.

            Returns:
                bool: True if all values match the expected type, False otherwise.
            """
            valid = True
            for entry in value:
                if not self.is_valid_value(entry, valuetype):
                    valid = False
                    break
            return valid

        if not isinstance(value, list) or not all_values_allowed(value, valuetype):
            return False

        if comparator == "BETWEEN" and len(value) == 2:
            return True

        elif comparator == "IN" and len(value) > 0:
            return True

        return False

    def is_valid_comparison(self, column: str, comparison: dict) -> bool:
        """Checks if a comparison operator and value are valid for a column.

        Validates that the comparator is a valid operator, and the value is the
        expected type for the column or a valid special comparison.

        Args:
            column (str): The column name.
            comparison (dict): The comparison operator and value.

        Returns:
            bool: True if the comparison is valid, False otherwise.
        """
        comparator = list(comparison)[0]

        if (
            comparator not in self.COMPARISON
            and comparator not in self.SPECIAL_COMPARISON
        ):
            return False

        value = comparison[comparator]
        column_type = self.ALLOWED_COLUMNS.get(
            column, self.ALLOWED_COLUMNS.get("*", object))
        if (self.is_valid_value(value, column_type) or
                self.is_special_comparison(comparator, value, column_type)):
            return True
        return False

    @staticmethod
    def get_sql_comparator(comparator: str) -> str:
        """
        Returns the SQL comparator, replacing '!=' with '<>' if necessary.

        Args:
            comparator (str): The original SQL comparator.

        Returns:
            str: The adjusted SQL comparator.
        """
        return comparator if comparator != "!=" else "<>"

    def is_value_in_allowed_categories(self, value: str) -> bool:
        """
        Checks if the given value is in the allowed categories.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if the value is in the allowed categories, False otherwise.
        """
        # Enhanced logic that supports our wildcard system
        is_valid_column = self._is_column_allowed(value)
        is_logical_operator = value in self.LOGICAL
        is_comparison_operator = (value in self.SPECIAL_COMPARISON or
                                  value in self.COMPARISON)

        return is_valid_column or is_logical_operator or is_comparison_operator

    def logic_parse(
        self, json_input: dict
    ) -> tuple[Literal[False], str] | tuple[Literal[True], str, tuple]:
        if len(json_input) == 0:
            return False, "Nothing To Compute"

        value: str = list(json_input.keys())[0]

        # Check if the value is in the allowed categories
        if not self.is_value_in_allowed_categories(value):
            return False, f"Invalid Input - {value}"

        elif value in self.LOGICAL and not isinstance(json_input[value], list):
            return False, f"Bad {value}, non list"

        elif value in self.ALLOWED_COLUMNS and not self.is_valid_comparison(
            value, json_input[value]
        ):
            if isinstance(json_input[value], dict):
                value0 = list(json_input[value])[0]
                if (
                    value0 not in self.COMPARISON
                    and value0 not in self.SPECIAL_COMPARISON
                ):
                    return False, f"Non Valid comparitor - {value0}"
            # Get the expected type for the column
            expected_type = self.ALLOWED_COLUMNS.get(
                value, self.ALLOWED_COLUMNS.get("*", object))
            return False, f"Bad {value}, non {expected_type}"

        if self.is_valid_comparison(value, json_input[value]):
            comparator = list(json_input[value])[0]

            adjusted_comparator = self.get_sql_comparator(comparator)

            if (
                comparator in self.COMPARISON
                and not self.is_another_column(json_input[value][comparator])
                and not isinstance(json_input[value][comparator], dict)
            ):
                return (
                    True,
                    f"{value} {adjusted_comparator} ?",
                    json_input[value][comparator]
                    if isinstance(json_input[value][comparator], tuple)
                    else (json_input[value][comparator],),
                )

            elif comparator in self.COMPARISON and self.is_another_column(
                json_input[value][comparator]
            ):
                return (
                    True,
                    f"{value} {adjusted_comparator} {json_input[value][comparator]}",
                    (),
                )

            elif list(json_input[value][comparator])[0] in self.AGGREGATES:
                # Extract the aggregate function name and its argument
                aggregate_function = list(json_input[value][comparator])[0]
                aggregate_argument = json_input[value][comparator][aggregate_function]

                return (
                    True,
                    f"{value} {adjusted_comparator} {aggregate_function}({aggregate_argument})",
                    (),
                )

            elif comparator in self.SPECIAL_COMPARISON:
                if comparator == "BETWEEN":
                    return (
                        True,
                        f"{value} BETWEEN ? AND ?",
                        tuple(json_input[value][comparator]),
                    )

                elif comparator == "IN":
                    # Determine the number of placeholders needed
                    num_placeholders = len(json_input[value][comparator])

                    # Generate the placeholders string
                    placeholders = (
                        "?"
                        if num_placeholders == 1
                        else ",".join(["?" for _ in range(num_placeholders)])
                    )

                    return (
                        True,
                        f"{value} IN ({placeholders})",
                        tuple(json_input[value][comparator]),
                    )

            return False, f"Comparitor Error - {comparator}"

        elif value in self.LOGICAL and isinstance(json_input[value], list):
            if len(json_input[value]) < 2:
                return False, "Invalid boolean length, must be >= 2"

            data = []
            safe = (True, "")
            for case in json_input[value]:
                evaluation = self.logic_parse(case)
                if not evaluation[0]:
                    safe = evaluation
                    break

                data.append(evaluation[1:])

            if not safe[0]:
                return safe

            params = []
            output = []
            for entry in data:
                if isinstance(entry[1], tuple):
                    for sub in entry[1]:
                        params.append(sub)
                else:
                    params.append(entry[1])
                output.append(entry[0])

            params = tuple(params)

            data = f"({f' {value.upper()} '.join(output)})"

            return True, data, params if isinstance(params, tuple) else (params,)

    def _validate_join_condition(self, condition: str) -> bool:
        """Validate JOIN ON condition for security."""
        if not condition or not isinstance(condition, str):
            return False

        # Check for suspicious patterns
        suspicious_patterns = [
            r';\s*DROP',
            r';\s*DELETE',
            r';\s*INSERT',
            r';\s*UPDATE',
            r'--',
            r'/\*',
            r'xp_',
            r'sp_'
        ]

        condition_upper = condition.upper()
        for pattern in suspicious_patterns:
            if re.search(pattern, condition_upper, re.IGNORECASE):
                return False

        return True

    def _parse_table_with_alias(self, table_input: Union[str, Dict]) -> Dict[str, str]:
        """Parse table input and return standardized format."""
        if isinstance(table_input, str):
            return {"table": table_input, "alias": None}
        elif isinstance(table_input, dict):
            return {
                "table": table_input.get("table", ""),
                "alias": table_input.get("alias", None)
            }
        else:
            raise ValueError(f"Invalid table format: {table_input}")

    def _build_table_clause(self, table_info: Dict[str, str]) -> str:
        """Build table clause with optional alias."""
        table_clause = table_info["table"]
        if table_info["alias"]:
            table_clause += f" AS {table_info['alias']}"
        return table_clause

    def _parse_joins(self, joins: List[Dict]) -> tuple[str, List[Any]]:
        """Parse JOIN clauses and return SQL and parameters."""
        if not joins:
            return "", []

        join_clauses = []
        all_params = []

        for join in joins:
            # Validate JOIN type
            join_type = join.get("type", "INNER JOIN").upper()
            if not self._is_entity_allowed(join_type, self.ALLOWED_JOINS, self.NOT_ALLOWED_JOINS):
                raise ValueError(f"JOIN type not allowed: {join_type}")

            # Parse target table
            table_info = self._parse_table_with_alias(join)
            if not self._is_entity_allowed(table_info["table"], self.ALLOWED_TABLES, self.NOT_ALLOWED_TABLES):
                raise ValueError(f"Table not allowed: {table_info['table']}")

            # Build JOIN clause
            table_clause = self._build_table_clause(table_info)

            # Handle ON condition
            on_condition = join.get("on", "")
            if on_condition and not self._validate_join_condition(on_condition):
                raise ValueError(f"Invalid JOIN condition: {on_condition}")

            join_clause = f"{join_type} {table_clause}"
            if on_condition:
                join_clause += f" ON {on_condition}"

            join_clauses.append(join_clause)

        return " ".join(join_clauses), all_params

    def sql_parse(
        self, json_input: dict, with_values: bool = False
    ) -> tuple[Literal[False], str] | tuple[Literal[True], str, tuple]:
        """
        Enhanced SQL parser with full JOIN support.

        Args:
            json_input (dict): JSON input containing query structure
            with_values (bool): If True, returns SQL with actual values instead of placeholders

        Supports both legacy format and new extended format:

        Legacy format (backward compatible):
        {
            "query": "SELECT",
            "items": ["*"],
            "table": "users",
            "connection": "WHERE",
            "logic": {"id": {"=": 1}}
        }

        Extended format (with JOINs):
        {
            "query": "SELECT",
            "items": ["u.name", "r.role_name"],
            "from": {"table": "users", "alias": "u"},
            "joins": [
                {
                    "type": "INNER JOIN",
                    "table": "roles",
                    "alias": "r",
                    "on": "u.role_id = r.id"
                }
            ],
            "where": {"u.id": {"=": 1}},
            "group_by": ["u.id"],
            "having": {"COUNT(*)": {">": 1}},
            "order_by": [{"column": "u.name", "direction": "ASC"}],
            "limit": 10,
            "offset": 0
        }

        Returns:
            tuple[bool, str, tuple]: (success, sql, params) or (False, error_message, ())
        """

        try:
            # Validate required fields
            if "query" not in json_input:
                return False, "Missing required field: query", ()
            if "items" not in json_input:
                return False, "Missing required field: items", ()

            # Validate query type
            query = json_input["query"]
            if not self._is_entity_allowed(query, self.ALLOWED_QUERIES, self.NOT_ALLOWED_QUERIES):
                return False, f"Query not allowed: {query}", ()

            # Validate items
            items = json_input["items"]
            if not isinstance(items, list):
                return False, "Items must be a list", ()

            for item in items:
                item_name = item if isinstance(item, str) else str(item)
                if not self._is_entity_allowed(item_name, self.ALLOWED_ITEMS, self.NOT_ALLOWED_ITEMS):
                    return False, f"Item not allowed: {item_name}", ()

            # Build SELECT clause
            select_clause = f"{query} {','.join(items)}"

            # Determine if using legacy or extended format
            is_extended = "from" in json_input or "joins" in json_input
            all_params = []

            if is_extended:
                # Extended format with JOIN support

                # Parse FROM clause
                from_clause = ""
                if "from" in json_input:
                    from_info = self._parse_table_with_alias(
                        json_input["from"])
                    if not self._is_entity_allowed(from_info["table"], self.ALLOWED_TABLES, self.NOT_ALLOWED_TABLES):
                        return False, f"Table not allowed: {from_info['table']}", ()
                    from_clause = f"FROM {self._build_table_clause(from_info)}"
                elif "table" in json_input:
                    # Fallback to legacy table format
                    table = json_input["table"]
                    if not self._is_entity_allowed(table, self.ALLOWED_TABLES, self.NOT_ALLOWED_TABLES):
                        return False, f"Table not allowed: {table}", ()
                    from_clause = f"FROM {table}"
                else:
                    return False, "Missing FROM clause (use 'from' or 'table')", ()

                # Parse JOINs
                join_clause = ""
                if "joins" in json_input:
                    join_clause, join_params = self._parse_joins(
                        json_input["joins"])
                    all_params.extend(join_params)

                # Parse WHERE clause
                where_clause = ""
                if "where" in json_input:
                    where_condition, where_params = self._parse_logic_condition(
                        json_input["where"])
                    if where_condition:
                        where_clause = f"WHERE {where_condition}"
                        all_params.extend(where_params)
                elif "connection" in json_input and "logic" in json_input:
                    # Legacy WHERE support
                    connection = json_input["connection"]
                    if not self._is_entity_allowed(connection, self.ALLOWED_CONNECTIONS, self.NOT_ALLOWED_CONNECTIONS):
                        return False, f"Connection not allowed: {connection}", ()
                    logic_condition, logic_params = self._parse_logic_condition(
                        json_input["logic"])
                    if logic_condition:
                        where_clause = f"{connection} {logic_condition}"
                        all_params.extend(logic_params)

                # Parse GROUP BY
                group_by_clause = ""
                if "group_by" in json_input:
                    group_by = json_input["group_by"]
                    if isinstance(group_by, list):
                        group_by_clause = f"GROUP BY {','.join(group_by)}"

                # Parse HAVING
                having_clause = ""
                if "having" in json_input:
                    having_condition, having_params = self._parse_logic_condition(
                        json_input["having"])
                    if having_condition:
                        having_clause = f"HAVING {having_condition}"
                        all_params.extend(having_params)

                # Parse ORDER BY
                order_by_clause = ""
                if "order_by" in json_input:
                    order_by = json_input["order_by"]
                    if isinstance(order_by, list):
                        order_items = []
                        for item in order_by:
                            if isinstance(item, dict):
                                column = item.get("column", "")
                                direction = item.get(
                                    "direction", "ASC").upper()
                                if direction not in ["ASC", "DESC"]:
                                    direction = "ASC"
                                order_items.append(f"{column} {direction}")
                            else:
                                order_items.append(str(item))
                        if order_items:
                            order_by_clause = f"ORDER BY {','.join(order_items)}"

                # Parse LIMIT and OFFSET
                limit_clause = ""
                if "limit" in json_input:
                    limit = json_input["limit"]
                    if isinstance(limit, int) and limit > 0:
                        limit_clause = f"LIMIT {limit}"
                        if "offset" in json_input:
                            offset = json_input["offset"]
                            if isinstance(offset, int) and offset >= 0:
                                limit_clause += f" OFFSET {offset}"

                # Assemble final SQL
                sql_parts = [select_clause, from_clause, join_clause, where_clause,
                             group_by_clause, having_clause, order_by_clause, limit_clause]
                sql = " ".join([part for part in sql_parts if part])

            else:
                # Legacy format (backward compatibility)
                if "table" not in json_input:
                    return False, "Missing required field: table", ()

                table = json_input["table"]
                if not self._is_entity_allowed(table, self.ALLOWED_TABLES, self.NOT_ALLOWED_TABLES):
                    return False, f"Table not allowed: {table}", ()

                sql = f"{select_clause} FROM {table}"

                # Handle legacy WHERE clause
                if "connection" in json_input and "logic" in json_input:
                    connection = json_input["connection"]
                    if not self._is_entity_allowed(connection, self.ALLOWED_CONNECTIONS, self.NOT_ALLOWED_CONNECTIONS):
                        return False, f"Connection not allowed: {connection}", ()

                    logic_condition, logic_params = self._parse_logic_condition(
                        json_input["logic"])
                    if logic_condition:
                        sql += f" {connection} {logic_condition}"
                        all_params.extend(logic_params)

            # If with_values is True, substitute parameters with actual values
            if with_values and all_params:
                sql_with_values = sql
                for param in all_params:
                    # Handle different parameter types
                    if param is None:
                        sql_with_values = sql_with_values.replace(
                            '?', 'NULL', 1)
                    elif isinstance(param, str):
                        # Escape single quotes in strings
                        escaped_param = param.replace("'", "''")
                        sql_with_values = sql_with_values.replace(
                            '?', f"'{escaped_param}'", 1)
                    elif isinstance(param, (int, float)):
                        sql_with_values = sql_with_values.replace(
                            '?', str(param), 1)
                    elif isinstance(param, bool):
                        sql_with_values = sql_with_values.replace(
                            '?', 'TRUE' if param else 'FALSE', 1)
                    else:
                        # For other types, convert to string and quote
                        escaped_param = str(param).replace("'", "''")
                        sql_with_values = sql_with_values.replace(
                            '?', f"'{escaped_param}'", 1)
                return True, sql_with_values, ()

            return True, sql, tuple(all_params)

        except Exception as e:
            return False, f"Error parsing SQL: {str(e)}", ()

    def _parse_logic_condition(self, logic: Dict) -> tuple[str, List[Any]]:
        """Parse WHERE/HAVING logic conditions."""
        if not logic:
            return "", []

        # For now, handle simple conditions
        # In full implementation, integrate the original logic_parse method
        conditions = []
        params = []

        for column, condition in logic.items():
            if isinstance(condition, dict):
                for operator, value in condition.items():
                    if operator in self.COMPARISON:
                        conditions.append(f"{column} {operator} ?")
                        params.append(value)
                    elif operator in self.SPECIAL_COMPARISON:
                        if operator == "IN" and isinstance(value, list):
                            placeholders = ",".join(["?" for _ in value])
                            conditions.append(f"{column} IN ({placeholders})")
                            params.extend(value)
                        elif operator == "BETWEEN" and isinstance(value, list) and len(value) == 2:
                            conditions.append(f"{column} BETWEEN ? AND ?")
                            params.extend(value)
                        else:
                            conditions.append(f"{column} {operator} ?")
                            params.append(value)

        return " AND ".join(conditions), params

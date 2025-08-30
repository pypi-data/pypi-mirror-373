import pprint
import re
from collections.abc import Mapping
from typing import Any, Dict, List, Optional, Tuple, Union
from ..core.table import Query


class TableHelper:
    """
    A helper class used to build SQL queries with joined/aliased tables,
    including foreign key expansions, pointer syntax, etc.

    This class is database-agnostic. Database-specific reserved words and operators
    should be set as class attributes by the database implementation modules.
    """

    # Reserved words that need quoting - set by database implementation
    reserved = []

    # SQL operators with their symbols - set by database implementation
    operators = {}

    def __init__(self, tx, table: str):
        """
        Initialize TableHelper.

        Args:
            tx: Database transaction object
            table: The main table name for this query
        """
        self.tx = tx
        self.letter = 65  # Start with 'A' for table aliases
        self.table_aliases = {}
        self.foreign_keys = {}
        self.current_table = table
        self.table_aliases["current_table"] = chr(self.letter)
        self.letter += 1

    def __str__(self):
        return "\n".join(
            f"{key}: {pprint.pformat(value)}" for key, value in vars(self).items()
        )

    def split_columns(self, query: str) -> List[str]:
        """
        Splits a string of comma-separated column expressions into a list, keeping parentheses balanced.

        Args:
            query: Comma-separated column expression string

        Returns:
            List of individual column expressions
        """
        if not isinstance(query, str):
            raise TypeError(f"Query must be a string, got {type(query)}")

        columns = []
        balance = 0
        current = []

        for char in query:
            if char == "," and balance == 0:
                column = "".join(current).strip()
                if column:  # Don't add empty columns
                    columns.append(column)
                current = []
            else:
                if char == "(":
                    balance += 1
                elif char == ")":
                    balance -= 1
                current.append(char)

        # Add the last column
        if current:
            column = "".join(current).strip()
            if column:
                columns.append(column)

        return columns

    def requires_joins(self) -> bool:
        """Check if this query requires table joins."""
        return len(self.table_aliases) > 1

    def has_pointer(self, column: str) -> bool:
        """
        Checks if there's an '>' in the column that indicates a pointer reference, e.g. 'local_column>foreign_column'.

        Args:
            column: The column string to check

        Returns:
            bool: True if column contains pointer syntax

        Raises:
            ValueError: If column format is invalid
        """
        if not isinstance(column, str):
            raise ValueError(f"Column must be a string, got {type(column)}")

        if not re.search(r"^[a-zA-Z0-9_>*]", column):
            raise ValueError(f"Invalid column specified: {column}")

        return bool(re.search(r"[a-zA-Z0-9_]+>[a-zA-Z0-9_]+", column))

    def __fetch_foreign_data(self, key: str) -> Dict[str, Any]:
        """
        Fetch foreign key information for a given key.

        Args:
            key: The foreign key string in format 'local_column>foreign_column'

        Returns:
            Dict containing foreign key metadata

        Raises:
            ValueError: If foreign key is not properly defined
        """
        if key in self.foreign_keys:
            return self.foreign_keys[key]

        if ">" not in key:
            raise ValueError(
                f"Invalid foreign key format: {key}. Expected 'local>foreign'"
            )

        local_column, foreign_column = key.split(">", 1)  # Split only on first >

        try:
            foreign = self.tx.table(self.current_table).foreign_key_info(local_column)
        except Exception as e:
            raise ValueError(f"Error fetching foreign key info for {local_column}: {e}")

        if not foreign:
            raise ValueError(
                f"Foreign key `{self.current_table}.{local_column}>{foreign_column}` not defined."
            )

        ref_table = foreign["referenced_table_name"]
        ref_schema = foreign["referenced_table_schema"]
        ref_column = foreign["referenced_column_name"]

        if ref_table not in self.table_aliases:
            if self.letter > 90:  # Z is ASCII 90
                raise ValueError("Too many table aliases - limit of 26 tables exceeded")
            self.table_aliases[ref_table] = chr(self.letter)
            self.letter += 1

        alias = self.table_aliases[ref_table]
        data = {
            "alias": alias,
            "ref_table": ref_table,
            "ref_schema": ref_schema,
            "local_column": local_column,
            "ref_column": ref_column,
        }
        self.foreign_keys[key] = data
        return data

    def resolve_references(
        self, key: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Resolves pointer syntax or table alias references.

        Args:
            key: The column key that may contain pointer syntax (e.g., 'local>foreign')
            options: Dictionary controlling aliasing behavior:
                - alias_column: Whether to add column aliases
                - alias_table: Whether to prefix with table aliases
                - alias_only: Whether to return only the alias name
                - bypass_on_error: Whether to return original key on errors

        Returns:
            Resolved column reference with appropriate aliasing

        Raises:
            ValueError: If key is invalid and bypass_on_error is False
        """
        if not key or not isinstance(key, str):
            if options and options.get("bypass_on_error"):
                return key or ""
            raise ValueError(f"Invalid key: {key}")

        if options is None:
            options = {"alias_column": True, "alias_table": False, "alias_only": False}

        # Remove operator first, then extract column name
        key_without_operator = self.remove_operator(key)
        column = self.extract_column_name(key_without_operator)
        if not column:
            if options.get("bypass_on_error"):
                return key
            raise ValueError(f"Could not extract column name from: {key}")

        alias = self.get_table_alias("current_table")
        if not self.has_pointer(column):
            # Standard column - no pointer syntax
            if (
                options.get("alias_table")
                and alias
                and alias != self.table_aliases.get("current_table", "A")
            ):
                name = f"{alias}.{self.quote(column)}"
            else:
                name = self.quote(column)
            # Safely replace only the column part, preserving operators
            return self.remove_operator(key).replace(column, name, 1)

        # Handle pointer syntax (local_column>foreign_column)
        pointer_parts = column.split(">", 1)  # Split only on first >
        if len(pointer_parts) != 2:
            if options.get("bypass_on_error"):
                return key
            raise ValueError(f"Invalid pointer syntax in column: {column}")

        local_column, foreign_column = pointer_parts
        local_column = local_column.strip()
        foreign_column = foreign_column.strip()

        if not local_column or not foreign_column:
            if options.get("bypass_on_error"):
                return key
            raise ValueError(f"Invalid pointer syntax - empty parts in: {column}")

        if options.get("alias_only"):
            return f"{local_column}_{foreign_column}"

        try:
            data = self.__fetch_foreign_data(column)
        except Exception as e:
            if options.get("bypass_on_error"):
                return key
            raise ValueError(f"Failed to resolve foreign key reference '{column}': {e}")

        # Build the foreign table reference
        if options.get("alias_table"):
            foreign_alias = self.get_table_alias(data["ref_table"])
            if not foreign_alias:
                if options.get("bypass_on_error"):
                    return key
                raise ValueError(
                    f"No alias found for foreign table: {data['ref_table']}"
                )
            name = f"{foreign_alias}.{self.quote(foreign_column)}"
        else:
            name = f"{data['ref_table']}.{self.quote(foreign_column)}"

        # Replace the column part and add alias if requested
        result = self.remove_operator(key).replace(column, name, 1)
        if options.get("alias_column"):
            result += f" AS {local_column}_{foreign_column}"

        return result

    def get_operator(self, key: str, val: Any) -> str:
        """
        Determines the SQL operator from the start of `key` or defaults to '='.

        Args:
            key: The key string that may contain an operator prefix
            val: The value (used for context in operator determination)

        Returns:
            str: The SQL operator to use

        Raises:
            ValueError: If key is invalid or operator is unsafe
        """
        if not isinstance(key, str):
            raise ValueError(f"Key must be a string, got {type(key)}")

        # Sanitize the key to prevent injection
        sanitized_key = " ".join(key.replace('"', "").split())

        for symbol, operator in self.operators.items():
            if sanitized_key.startswith(symbol):
                # Basic validation that the operator is safe
                if not re.match(r"^[A-Z\s<>=!]+$", operator):
                    raise ValueError(f"Unsafe operator detected: {operator}")
                return operator
        return "="

    def remove_operator(self, key: str) -> str:
        """
        Strips recognized operator symbols from the start of `key`.

        Args:
            key: The key string that may contain an operator prefix

        Returns:
            Key with operator prefix removed
        """
        if not isinstance(key, str):
            return key

        for symbol in self.operators.keys():
            if key.startswith(symbol):
                return key.replace(symbol, "", 1)
        return key

    def extract_column_name(self, sql_expression):
        """
        Extracts the 'bare' column name from a SQL expression.

        Supports:
        - Aliases (AS ...)
        - Window functions (OVER(... ORDER BY ...))
        - CAST(... AS ...)
        - CASE WHEN ... THEN ... ELSE ... END
        - Nested function calls
        - Grabs column from inside expressions (e.g. PLAID_ERROR from SUM(CASE...))

        Args:
            sql_expression (str): SQL expression (SELECT column) string.

        Returns:
            str or None: Extracted column name or None if undetectable.
        """
        expr = sql_expression.replace('"', "").strip()

        # Remove trailing alias
        expr = re.sub(r"(?i)\s+as\s+\w+$", "", expr).strip()

        # If OVER clause: extract column inside ORDER BY
        over_match = re.search(r"(?i)OVER\s*\(\s*ORDER\s+BY\s+([^\s,)]+)", expr)
        if over_match:
            return over_match.group(1)

        # Remove CAST(... AS ...)
        while re.search(r"(?i)CAST\s*\(([^()]+?)\s+AS\s+[^\)]+\)", expr):
            expr = re.sub(r"(?i)CAST\s*\(([^()]+?)\s+AS\s+[^\)]+\)", r"\1", expr)

        # Remove CASE WHEN ... THEN ... ELSE ... END, keep just the WHEN part
        while re.search(
            r"(?i)CASE\s+WHEN\s+(.+?)\s+THEN\s+.+?(?:\s+ELSE\s+.+?)?\s+END", expr
        ):
            expr = re.sub(
                r"(?i)CASE\s+WHEN\s+(.+?)\s+THEN\s+.+?(?:\s+ELSE\s+.+?)?\s+END",
                r"\1",
                expr,
            )

        # Unwrap function calls (SUM(...), MAX(...), etc.)
        while re.search(r"\b\w+\s*\(([^()]+)\)", expr):
            expr = re.sub(r"\b\w+\s*\(([^()]+)\)", r"\1", expr)

        # If multiple columns, take the first
        if "," in expr:
            expr = expr.split(",")[0].strip()

        # Extract column name (basic or dotted like table.col or *)
        # Handle asterisk separately since \b doesn't work with non-word characters
        if expr.strip() == "*":
            return "*"

        # Check for pointer syntax (>)
        if ">" in expr:
            # For pointer syntax, return the whole expression
            pointer_match = re.search(r"([a-zA-Z_][\w]*>[a-zA-Z_][\w]*)", expr)
            if pointer_match:
                return pointer_match.group(1)

        match = re.search(
            r"\b([a-zA-Z_][\w]*\.\*|[a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)?)\b", expr
        )
        return match.group(1) if match else None

    def are_parentheses_balanced(self, expression: str) -> bool:
        """
        Checks if parentheses in `expression` are balanced.

        Args:
            expression: The expression to check

        Returns:
            bool: True if parentheses are balanced
        """
        stack = []
        opening = "({["
        closing = ")}]"
        matching = {")": "(", "}": "{", "]": "["}

        for char in expression:
            if char in opening:
                stack.append(char)
            elif char in closing:
                if not stack or stack.pop() != matching[char]:
                    return False
        return not stack

    def get_table_alias(self, table: str) -> Optional[str]:
        """
        Get the alias for a table.

        Args:
            table: The table name

        Returns:
            The table alias or None if not found
        """
        return self.table_aliases.get(table)

    def make_predicate(
        self, key: str, val: Any, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Any]:
        """
        Builds a piece of SQL and corresponding parameters for a WHERE/HAVING predicate based on `key`, `val`.

        Args:
            key: The column key (may include operator prefix)
            val: The value to compare against
            options: Dictionary of options for reference resolution

        Returns:
            Tuple of (sql_string, parameters)
        """
        if options is None:
            options = {"alias_table": True, "alias_column": False}

        column = self.resolve_references(key, options=options)
        op = self.get_operator(key, val)

        # Subquery?
        if isinstance(val, Query):
            if op in ("<>", "NOT"):
                return f"{column} NOT IN ({val})", val.params or None
            return f"{column} IN ({val})", val.params or None

        # Null / special markers
        if val is None or isinstance(val, bool) or val in ("@@INFINITY", "@@UNKNOWN"):
            if isinstance(val, str) and val.startswith("@@"):
                val = val[2:]
            if val is None:
                val = "NULL"
            if op == "<>":
                return f"{column} IS NOT {str(val).upper()}", None
            return f"{column} IS {str(val).upper()}", None

        # Lists / tuples => IN / NOT IN
        if isinstance(val, (list, tuple)) and "><" not in key:
            # Convert string numbers to integers if all values are numeric strings
            if val and all(isinstance(v, str) and v.isdigit() for v in val):
                try:
                    val = tuple(int(v) for v in val)
                except ValueError:
                    pass  # Keep as strings if conversion fails

            # Convert to tuple for better parameter handling
            val_tuple = tuple(val)

            if not val_tuple:  # Empty list/tuple
                if "!" in key:
                    return "1=1", None  # Empty NOT IN is always true
                else:
                    return "1=0", None  # Empty IN is always false

            # Use IN/NOT IN for better type compatibility
            if "!" in key:
                placeholders = ",".join(["%s"] * len(val_tuple))
                return f"{column} NOT IN ({placeholders})", val_tuple
            else:
                placeholders = ",".join(["%s"] * len(val_tuple))
                return f"{column} IN ({placeholders})", val_tuple

        # "@@" => pass as literal
        if isinstance(val, str) and val.startswith("@@") and val[2:]:
            return f"{column} {op} {val[2:]}", None

        # Between operators
        if op in ["BETWEEN", "NOT BETWEEN"]:
            if not isinstance(val, (list, tuple)) or len(val) != 2:
                raise ValueError(
                    f"BETWEEN operator requires exactly 2 values, got {val}"
                )
            return f"{column} {op} %s and %s", tuple(val)

        # Default single-parameter predicate
        return f"{column} {op} %s", val

    def make_where(
        self, where: Union[Dict[str, Any], List[Tuple[str, Any]], str, None]
    ) -> Tuple[str, Tuple[Any, ...]]:
        """
        Converts various WHERE clause formats into SQL string and parameter values.

        Args:
            where: WHERE conditions in one of these formats:
                - Dict: {column: value} pairs that become "column = value" predicates
                - List of tuples: [(predicate_sql, params), ...] for pre-built predicates
                - String: Raw SQL WHERE clause (parameters not extracted)
                - None: No WHERE clause

        Returns:
            Tuple of (sql_string, parameter_tuple):
                - sql_string: Complete WHERE clause including "WHERE" keyword, or empty string
                - parameter_tuple: Tuple of parameter values for placeholder substitution

        Raises:
            ValueError: If where format is invalid or predicate generation fails
            TypeError: If where is an unsupported type
        """
        if not where:
            return "", tuple()

        # Convert dict to list of predicates
        if isinstance(where, Mapping):
            if not where:  # Empty dict
                return "", tuple()

            predicate_list = []
            for key, val in where.items():
                if not isinstance(key, str):
                    raise ValueError(
                        f"WHERE clause keys must be strings, got {type(key)}: {key}"
                    )
                try:
                    predicate_list.append(self.make_predicate(key, val))
                except Exception as e:
                    raise ValueError(f"Failed to create predicate for '{key}': {e}")
            where = predicate_list

        # Handle string WHERE clause (pass through as-is)
        elif isinstance(where, str):
            where_clause = where.strip()
            if not where_clause:
                return "", tuple()
            # Add WHERE keyword if not present
            if not where_clause.upper().startswith("WHERE"):
                where_clause = f"WHERE {where_clause}"
            return where_clause, tuple()

        # Validate list format
        elif isinstance(where, (list, tuple)):
            if not where:  # Empty list
                return "", tuple()

            # Validate each predicate tuple
            for i, item in enumerate(where):
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    raise ValueError(
                        f"WHERE predicate {i} must be a 2-element tuple (sql, params), got: {item}"
                    )
                sql_part, params = item
                if not isinstance(sql_part, str):
                    raise ValueError(
                        f"WHERE predicate {i} SQL must be a string, got {type(sql_part)}: {sql_part}"
                    )
        else:
            raise TypeError(
                f"WHERE clause must be dict, list, string, or None, got {type(where)}: {where}"
            )

        # Build final SQL and collect parameters
        sql_parts = ["WHERE"]
        vals = []

        for i, (pred_sql, pred_val) in enumerate(where):
            if i > 0:  # Add AND between predicates
                sql_parts.append("AND")

            sql_parts.append(pred_sql)

            # Handle parameter values
            if pred_val is not None:
                if isinstance(pred_val, tuple):
                    vals.extend(pred_val)
                else:
                    vals.append(pred_val)

        return " ".join(sql_parts), tuple(vals)

    @classmethod
    def quote(cls, data: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Class method version of quote for backward compatibility.
        Quotes identifiers (columns/tables) if needed, especially if they match reserved words or contain special chars.

        Args:
            data: String identifier or list of identifiers to quote

        Returns:
            Quoted identifier(s)
        """
        if isinstance(data, list):
            return [cls.quote(item) for item in data]

        if not isinstance(data, str):
            raise ValueError(f"Data must be string or list, got {type(data)}")

        # Handle special markers
        if data.startswith("@@"):
            return data[2:]

        parts = data.split(".")
        quoted_parts = []

        for part in parts:
            if not part:  # Skip empty parts
                continue

            # Skip if already quoted
            if part.startswith('"') and part.endswith('"'):
                quoted_parts.append(part)
            # Quote if reserved word, contains special chars, or starts with digit
            elif (
                part.upper() in cls.reserved
                or re.search(r"[/\-\s]", part)
                or (part and part[0].isdigit())
            ):
                # Escape any existing quotes in the identifier
                escaped_part = part.replace('"', '""')
                quoted_parts.append(f'"{escaped_part}"')
            else:
                quoted_parts.append(part)

        return ".".join(quoted_parts)

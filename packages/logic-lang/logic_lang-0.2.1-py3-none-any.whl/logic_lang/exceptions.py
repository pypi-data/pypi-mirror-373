"""
Custom exceptions for the logic language system.
"""

from typing import List


class RuleLanguageError(Exception):
    """Base exception for all logic language errors."""

    pass


class ParseError(RuleLanguageError):
    """Raised when there's a syntax error in the rule script."""

    def __init__(self, message: str, line: int = None, column: int = None):
        self.line = line
        self.column = column
        if line is not None:
            message = f"Line {line}: {message}"
        if column is not None:
            message = f"{message} (column {column})"
        super().__init__(message)


class InterpreterError(RuleLanguageError):
    """Raised when there's an error during rule execution."""

    pass


class VariableNotFoundError(InterpreterError):
    """Raised when referencing an undefined variable."""

    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        super().__init__(f"Variable '{variable_name}' is not defined")


class MissingExpectedVariableError(InterpreterError):
    """Raised when expected variables are not provided in features."""

    def __init__(
        self, missing_variables: List[str], expected_variables: List[str] = None
    ):
        self.missing_variables = missing_variables
        self.expected_variables = expected_variables
        message = f"Missing expected variables: {', '.join(missing_variables)}"
        if expected_variables:
            message = f"{message}. The script expects: {', '.join(expected_variables)}"
        super().__init__(message)


class TypeMismatchError(InterpreterError):
    """Raised when there's a type mismatch in operations."""

    def __init__(self, expected: str, actual: str, operation: str = None):
        self.expected = expected
        self.actual = actual
        self.operation = operation
        message = f"Expected {expected}, got {actual}"
        if operation:
            message = f"{message} in {operation}"
        super().__init__(message)


class UnsupportedOperationError(InterpreterError):
    """Raised when attempting an unsupported operation."""

    def __init__(self, operation: str, operand_types: str = None):
        self.operation = operation
        self.operand_types = operand_types
        message = f"Unsupported operation: {operation}"
        if operand_types:
            message = f"{message} on {operand_types}"
        super().__init__(message)


class InvalidFunctionError(InterpreterError):
    """Raised when calling an undefined or invalid function."""

    def __init__(self, function_name: str, available_functions: list = None):
        self.function_name = function_name
        self.available_functions = available_functions
        message = f"Unknown function: '{function_name}'"
        if available_functions:
            message = (
                f"{message}. Available functions: {', '.join(available_functions)}"
            )
        super().__init__(message)

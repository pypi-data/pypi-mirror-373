"""
Interpreter for the logic language.

Executes parsed AST to generate constraint objects using the soft logic framework.
The interpreter maintains a variable environment and provides built-in functions
for common constraint patterns.
"""

from typing import Callable, Dict, Any, List, Union, Optional, Tuple
import torch
from .soft_logic import (
    Truth,
    Constraint,
    ConstraintSet,
    sum_class_probabilities,
    exactly_one,
    mutual_exclusion,
    at_least_k,
    at_most_k,
    exactly_k,
    threshold_implication,
    conditional_probability,
    GodelSemantics,
    LukasiewiczSemantics,
    ProductSemantics,
    Semantics,
    _clamp01,
)
from .ast_nodes import *
from .exceptions import *

Tensor = torch.Tensor
TensorTruth = Union[Tensor, Truth]


class RuleInterpreter:
    """
    Interpreter for logic language scripts.

    The RuleInterpreter executes parsed AST to generate constraint objects using
    the soft logic framework. It maintains a variable environment and provides
    built-in functions for common constraint patterns.

    Built-in Functions:
    - Probability aggregation: sum, exactly_one, mutual_exclusion
    - Cardinality constraints: at_least_k, at_most_k, exactly_k
    - Logical operations: threshold_implication, conditional_probability
    - Comparison functions: greater_than, less_than, equals, threshold_constraint
    - Utility functions: clamp, threshold

    Example:
        >>> interpreter = RuleInterpreter()
        >>> features = {"predictions": torch.tensor([[0.8, 0.1, 0.1]])}
        >>> script = "constraint exactly_one(predictions);"
        >>> constraint_set = interpreter.execute(script, features)
    """

    def __init__(
        self, default_semantics: Optional[Semantics] = None, default_eps: float = 1e-6
    ):
        self.variables: Dict[str, Any] = {}
        self.constraints: List[Constraint] = []
        self.expected_variables: List[str] = []  # Track expected variables
        self.default_semantics = default_semantics or GodelSemantics(eps=default_eps)
        self.default_eps = default_eps

        # Built-in functions
        self.builtin_functions = {
            # Probability aggregation functions
            "sum": self._sum_function,
            "exactly_one": self._exactly_one_function,
            "mutual_exclusion": self._mutual_exclusion_function,
            # Cardinality constraint functions
            "at_least_k": self._at_least_k_function,
            "at_most_k": self._at_most_k_function,
            "exactly_k": self._exactly_k_function,
            # Logical implication and conditional functions
            "threshold_implication": self._threshold_implication_function,
            "conditional_probability": self._conditional_probability_function,
            # Comparison and threshold functions
            "greater_than": self._greater_than_function,
            "less_than": self._less_than_function,
            "equals": self._equals_function,
            "threshold_constraint": self._threshold_constraint_function,
            # Utility functions
            "clamp": self._clamp_function,
            "threshold": self._threshold_function,
        }

    def execute(
        self, script: str, features: Dict[str, torch.Tensor] = None
    ) -> ConstraintSet:
        """
        Execute a rule script and return constraint set.

        Args:
            script: Logic language script text
            features: Dictionary of feature tensors (e.g., from model output)

        Returns:
            ConstraintSet containing all defined constraints
        """
        from .parser import RuleParser

        # Reset state
        self.constraints = []
        self.expected_variables = []

        # Parse script first to collect expect statements
        parser = RuleParser()
        ast = parser.parse(script)

        # First pass: collect expected variables and set up aliases
        for statement in ast.statements:
            if isinstance(statement, ExpectStatement):
                for var in statement.variables:
                    if isinstance(var, tuple):
                        # Variable with alias: (original_name, alias)
                        original_name, alias = var
                        if (
                            original_name not in self.expected_variables
                        ):  # Avoid duplicates
                            self.expected_variables.append(original_name)
                    else:
                        # Variable without alias
                        if var not in self.expected_variables:  # Avoid duplicates
                            self.expected_variables.append(var)

        # Validate that all expected variables are provided
        if features is None:
            features = {}

        missing_variables = []
        for expected_var in self.expected_variables:
            if expected_var not in features:
                missing_variables.append(expected_var)

        if missing_variables:
            raise MissingExpectedVariableError(
                missing_variables, self.expected_variables
            )

        # Initialize with provided features
        self.variables.update(features)

        # Second pass: set up aliases for variables
        for statement in ast.statements:
            if isinstance(statement, ExpectStatement):
                for var in statement.variables:
                    if isinstance(var, tuple):
                        # Variable with alias: (original_name, alias)
                        original_name, alias = var
                        if original_name in self.variables:
                            # Create alias in the variable environment
                            self.variables[alias] = self.variables[original_name]

        # Execute statements
        for statement in ast.statements:
            self._execute_statement(statement)

        return ConstraintSet(self.constraints)

    def _execute_statement(self, stmt: Statement) -> None:
        """Execute a single statement."""
        if isinstance(stmt, CommentStatement):
            # Comments are ignored
            pass
        elif isinstance(stmt, ConstStatement):
            # Evaluate constant expression to get the value
            if hasattr(stmt.value, "__class__") and hasattr(stmt.value, "__module__"):
                # It's an AST expression, evaluate it
                value = self._evaluate_expression(stmt.value)
            else:
                # It's already a literal value (backward compatibility)
                value = stmt.value

            # Ensure the result is a constant (number, string, or list-like)
            if not isinstance(value, (int, float, str, list)):
                raise InterpreterError(
                    f"Constants must evaluate to numbers, strings, or list-like objects, got {type(value).__name__}"
                )

            self.variables[stmt.name] = value
        elif isinstance(stmt, DefineStatement):
            value = self._evaluate_expression(stmt.expression)
            self.variables[stmt.name] = value
        elif isinstance(stmt, ExpectStatement):
            # Handle variable aliasing during execution
            for var in stmt.variables:
                if isinstance(var, tuple):
                    # Variable with alias: (original_name, alias)
                    original_name, alias = var
                    if original_name in self.variables:
                        # Create alias in the variable environment
                        self.variables[alias] = self.variables[original_name]
                    # Track expected variable (avoid duplicates)
                    if original_name not in self.expected_variables:
                        self.expected_variables.append(original_name)
                else:
                    # Variable without alias - just track it
                    if var not in self.expected_variables:
                        self.expected_variables.append(var)
        elif isinstance(stmt, ConstraintStatement):
            self._execute_constraint(stmt)
        else:
            raise InterpreterError(f"Unknown statement type: {type(stmt)}")

    def _execute_constraint(self, stmt: ConstraintStatement) -> None:
        """Execute a constraint statement."""
        # Evaluate the constraint expression
        expr_value = self._evaluate_expression(stmt.expression)

        # Extract parameters
        weight = 1.0
        if stmt.weight:
            weight_val = self._evaluate_expression(stmt.weight)
            if isinstance(weight_val, (int, float)):
                weight = float(weight_val)
            else:
                raise TypeMismatchError(
                    "number", type(weight_val).__name__, "weight parameter"
                )

        transform = "logbarrier"
        if stmt.transform:
            transform_val = self._evaluate_expression(stmt.transform)
            if isinstance(transform_val, str):
                transform = transform_val
            else:
                raise TypeMismatchError(
                    "string", type(transform_val).__name__, "transform parameter"
                )

        # Additional parameters
        params = {}
        if stmt.params:
            for key, param_expr in stmt.params.items():
                params[key] = self._evaluate_expression(param_expr)

        # Create constraint based on expression type
        if isinstance(expr_value, Truth):
            # Direct Truth object - create constraint
            constraint = Constraint(
                expr_value, transform=transform, weight=weight, **params
            )
            self.constraints.append(constraint)
        elif hasattr(expr_value, "__call__"):
            # Function that returns a constraint
            constraint = expr_value(weight=weight, transform=transform, **params)
            self.constraints.append(constraint)
        else:
            raise InterpreterError(f"Cannot create constraint from {type(expr_value)}")

    def _evaluate_expression(self, expr: Expression) -> Any:
        """Evaluate an expression and return its value."""
        if isinstance(expr, Identifier):
            if expr.name not in self.variables:
                raise VariableNotFoundError(expr.name)
            return self.variables[expr.name]

        elif isinstance(expr, NumberLiteral):
            return expr.value

        elif isinstance(expr, StringLiteral):
            return expr.value

        elif isinstance(expr, ListLiteral):
            return [self._evaluate_expression(elem) for elem in expr.elements]

        elif isinstance(expr, BinaryOp):
            return self._evaluate_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            return self._evaluate_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            return self._evaluate_function_call(expr)

        elif isinstance(expr, IndexExpression):
            return self._evaluate_index_expression(expr)

        elif isinstance(expr, SliceExpression):
            return self._evaluate_slice_expression(expr)

        else:
            raise InterpreterError(f"Unknown expression type: {type(expr)}")

    def _evaluate_binary_op(self, expr: BinaryOp) -> Any:
        """Evaluate binary operations."""
        left = self._evaluate_expression(expr.left)
        right = self._evaluate_expression(expr.right)

        # Handle pure numeric operations first (for constant definitions)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if expr.operator == ">":
                return float(left > right)
            elif expr.operator == "<":
                return float(left < right)
            elif expr.operator == "==":
                return float(left == right)
            elif expr.operator == ">=":
                return float(left >= right)
            elif expr.operator == "<=":
                return float(left <= right)
            elif expr.operator == "+":
                return left + right
            elif expr.operator == "-":
                return left - right
            elif expr.operator == "*":
                return left * right
            elif expr.operator == "/":
                if right == 0:
                    raise InterpreterError("Division by zero")
                return left / right
            else:
                # For logical operations, convert to Truth objects
                left = Truth(torch.tensor(float(left)), self.default_semantics)
                right = Truth(torch.tensor(float(right)), self.default_semantics)

        # Handle arithmetic operations on tensors (before converting to Truth)
        elif expr.operator in ["+", "-", "*", "/"]:
            # Ensure we have compatible types for arithmetic
            if isinstance(left, (int, float)) and isinstance(right, torch.Tensor):
                left = torch.full_like(right, float(left))
            elif isinstance(right, (int, float)) and isinstance(left, torch.Tensor):
                right = torch.full_like(left, float(right))
            elif isinstance(left, Truth) and isinstance(right, torch.Tensor):
                # Truth * Tensor operations
                if expr.operator == "+":
                    return Truth(left.value + right, left.semantics)
                elif expr.operator == "-":
                    return Truth(left.value - right, left.semantics)
                elif expr.operator == "*":
                    return Truth(left.value * right, left.semantics)
                elif expr.operator == "/":
                    if torch.any(right == 0):
                        raise InterpreterError("Division by zero")
                    return Truth(left.value / right, left.semantics)
            elif isinstance(left, torch.Tensor) and isinstance(right, Truth):
                # Tensor * Truth operations
                if expr.operator == "+":
                    return Truth(left + right.value, right.semantics)
                elif expr.operator == "-":
                    return Truth(left - right.value, right.semantics)
                elif expr.operator == "*":
                    return Truth(left * right.value, right.semantics)
                elif expr.operator == "/":
                    if torch.any(right.value == 0):
                        raise InterpreterError("Division by zero")
                    return Truth(left / right.value, right.semantics)
            elif isinstance(left, (int, float)) and isinstance(right, Truth):
                if expr.operator == "+":
                    return Truth(left + right.value, right.semantics)
                elif expr.operator == "-":
                    return Truth(left - right.value, right.semantics)
                elif expr.operator == "*":
                    return Truth(left * right.value, right.semantics)
                elif expr.operator == "/":
                    # Check for division by zero in Truth objects
                    if torch.any(right.value == 0):
                        raise InterpreterError("Division by zero")
                    return Truth(left / right.value, right.semantics)
            elif isinstance(right, (int, float)) and isinstance(left, Truth):
                if expr.operator == "+":
                    return Truth(left.value + right, left.semantics)
                elif expr.operator == "-":
                    return Truth(left.value - right, left.semantics)
                elif expr.operator == "*":
                    return Truth(left.value * right, left.semantics)
                elif expr.operator == "/":
                    if right == 0:
                        raise InterpreterError("Division by zero")
                    return Truth(left.value / right, left.semantics)
            elif isinstance(left, Truth) and isinstance(right, Truth):
                if expr.operator == "+":
                    return Truth(left.value + right.value, left.semantics)
                elif expr.operator == "-":
                    return Truth(left.value - right.value, left.semantics)
                elif expr.operator == "*":
                    return Truth(left.value * right.value, left.semantics)
                elif expr.operator == "/":
                    # Check for division by zero in Truth objects
                    if torch.any(right.value == 0):
                        raise InterpreterError("Division by zero")
                    return Truth(left.value / right.value, left.semantics)

            # Pure tensor arithmetic - return tensor, not Truth
            if isinstance(left, torch.Tensor) and isinstance(right, torch.Tensor):
                if expr.operator == "+":
                    return left + right
                elif expr.operator == "-":
                    return left - right
                elif expr.operator == "*":
                    return left * right
                elif expr.operator == "/":
                    # Check for division by zero in tensors
                    if torch.any(right == 0):
                        raise InterpreterError("Division by zero")
                    return left / right

        # For logical and comparison operations, ensure we have Truth objects
        # Handle mixed types: convert numbers to tensors when needed
        if isinstance(left, (int, float)) and isinstance(right, torch.Tensor):
            # Convert scalar to tensor with same shape as the tensor operand
            left = torch.full_like(right, float(left))
        elif isinstance(right, (int, float)) and isinstance(left, torch.Tensor):
            # Convert scalar to tensor with same shape as the tensor operand
            right = torch.full_like(left, float(right))
        elif isinstance(left, (int, float)) and isinstance(right, Truth):
            # Convert scalar to tensor with same shape as the Truth value
            left = torch.full_like(right.value, float(left))
        elif isinstance(right, (int, float)) and isinstance(left, Truth):
            # Convert scalar to tensor with same shape as the Truth value
            right = torch.full_like(left.value, float(right))

        # Convert tensors to Truth objects for logical operations
        if isinstance(left, torch.Tensor):
            left = Truth(_clamp01(left, self.default_eps), self.default_semantics)
        if isinstance(right, torch.Tensor):
            right = Truth(_clamp01(right, self.default_eps), self.default_semantics)

        # Logical operations - ensure both operands are Truth objects
        if expr.operator == "|":  # OR
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left | right
            else:
                raise UnsupportedOperationError(
                    f"OR operation", f"{type(left).__name__} | {type(right).__name__}"
                )

        elif expr.operator == "&":  # AND
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left & right
            else:
                raise UnsupportedOperationError(
                    f"AND operation", f"{type(left).__name__} & {type(right).__name__}"
                )

        elif expr.operator == "^":  # XOR
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left ^ right
            else:
                raise UnsupportedOperationError(
                    f"XOR operation", f"{type(left).__name__} ^ {type(right).__name__}"
                )

        elif expr.operator == ">>":  # IMPLIES
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left >> right
            else:
                raise UnsupportedOperationError(
                    f"IMPLIES operation",
                    f"{type(left).__name__} >> {type(right).__name__}",
                )

        elif expr.operator == ">":  # GREATER THAN
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left > right
            else:
                raise UnsupportedOperationError(
                    f"GT operation", f"{type(left).__name__} > {type(right).__name__}"
                )

        elif expr.operator == "<":  # LESS THAN
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left < right
            else:
                raise UnsupportedOperationError(
                    f"LT operation", f"{type(left).__name__} < {type(right).__name__}"
                )

        elif expr.operator == "==":  # EQUALS
            if isinstance(left, Truth) and isinstance(right, Truth):
                return left.eq(
                    right
                )  # Use .eq() method to avoid Python equality conflicts
            else:
                raise UnsupportedOperationError(
                    f"EQ operation", f"{type(left).__name__} == {type(right).__name__}"
                )

        elif expr.operator == ">=":  # GREATER THAN OR EQUAL
            if isinstance(left, Truth) and isinstance(right, Truth):
                return (left > right) | (left.eq(right))
            else:
                raise UnsupportedOperationError(
                    f"GTE operation", f"{type(left).__name__} >= {type(right).__name__}"
                )

        elif expr.operator == "<=":  # LESS THAN OR EQUAL
            if isinstance(left, Truth) and isinstance(right, Truth):
                return (left < right) | (left.eq(right))
            else:
                raise UnsupportedOperationError(
                    f"LTE operation", f"{type(left).__name__} <= {type(right).__name__}"
                )

        else:
            raise UnsupportedOperationError(f"Unknown binary operator: {expr.operator}")

    def _evaluate_unary_op(self, expr: UnaryOp) -> Any:
        """Evaluate unary operations."""
        operand = self._evaluate_expression(expr.operand)

        if expr.operator == "~":  # NOT
            if isinstance(operand, torch.Tensor):
                operand = Truth(
                    _clamp01(operand, self.default_eps), self.default_semantics
                )

            if isinstance(operand, Truth):
                return ~operand
            else:
                raise UnsupportedOperationError(
                    f"NOT operation", type(operand).__name__
                )

        elif expr.operator == "&":  # AND_n across tensor dimensions
            if isinstance(operand, torch.Tensor):
                # Convert tensor to sequence of Truth objects along last dimension
                if operand.dim() == 0:
                    # Scalar tensor - just convert to Truth
                    return Truth(
                        _clamp01(operand, self.default_eps), self.default_semantics
                    )

                # Split tensor along last dimension into individual Truth objects
                truth_list = []
                for i in range(operand.size(-1)):
                    elem = operand[..., i]
                    truth_list.append(
                        Truth(_clamp01(elem, self.default_eps), self.default_semantics)
                    )

                if not truth_list:
                    raise UnsupportedOperationError("AND_n operation", "empty tensor")

                return Truth.AND_n(truth_list)

            elif isinstance(operand, Truth):
                # If it's already a Truth object with multiple dimensions, split along last dim
                if operand.value.dim() == 0:
                    # Scalar - return as is
                    return operand

                truth_list = []
                for i in range(operand.value.size(-1)):
                    elem = operand.value[..., i]
                    truth_list.append(
                        Truth(_clamp01(elem, self.default_eps), operand.semantics)
                    )

                if not truth_list:
                    raise UnsupportedOperationError(
                        "AND_n operation", "empty Truth tensor"
                    )

                return Truth.AND_n(truth_list)

            else:
                raise UnsupportedOperationError(
                    f"AND_n operation", type(operand).__name__
                )

        elif expr.operator == "|":  # OR_n across tensor dimensions
            if isinstance(operand, torch.Tensor):
                # Convert tensor to sequence of Truth objects along last dimension
                if operand.dim() == 0:
                    # Scalar tensor - just convert to Truth
                    return Truth(
                        _clamp01(operand, self.default_eps), self.default_semantics
                    )

                # Split tensor along last dimension into individual Truth objects
                truth_list = []
                for i in range(operand.size(-1)):
                    elem = operand[..., i]
                    truth_list.append(
                        Truth(_clamp01(elem, self.default_eps), self.default_semantics)
                    )

                if not truth_list:
                    raise UnsupportedOperationError("OR_n operation", "empty tensor")

                return Truth.OR_n(truth_list)

            elif isinstance(operand, Truth):
                # If it's already a Truth object with multiple dimensions, split along last dim
                if operand.value.dim() == 0:
                    # Scalar - return as is
                    return operand

                truth_list = []
                for i in range(operand.value.size(-1)):
                    elem = operand.value[..., i]
                    truth_list.append(
                        Truth(_clamp01(elem, self.default_eps), operand.semantics)
                    )

                if not truth_list:
                    raise UnsupportedOperationError(
                        "OR_n operation", "empty Truth tensor"
                    )

                return Truth.OR_n(truth_list)

            else:
                raise UnsupportedOperationError(
                    f"OR_n operation", type(operand).__name__
                )

        elif expr.operator == "-":  # UNARY MINUS
            if isinstance(operand, (int, float)):
                # Negate numeric constants
                return -operand
            elif isinstance(operand, torch.Tensor):
                # Negate tensor values
                return -operand
            elif isinstance(operand, Truth):
                # Negate the underlying tensor values and create new Truth object
                return Truth(-operand.value, operand.semantics)
            else:
                raise UnsupportedOperationError(
                    f"UNARY MINUS operation", type(operand).__name__
                )

        elif expr.operator == "+":  # UNARY PLUS
            if isinstance(operand, (int, float)):
                # Unary plus on numeric constants (no-op)
                return operand
            elif isinstance(operand, torch.Tensor):
                # Unary plus on tensor (no-op)
                return operand
            elif isinstance(operand, Truth):
                # Unary plus on Truth object (no-op)
                return operand
            else:
                raise UnsupportedOperationError(
                    f"UNARY PLUS operation", type(operand).__name__
                )

        else:
            raise UnsupportedOperationError(f"Unknown unary operator: {expr.operator}")

    def _evaluate_index_expression(self, expr: IndexExpression) -> Any:
        """Evaluate indexing operations like variable[0], tensor[:, 1]."""
        # Evaluate the object being indexed
        obj = self._evaluate_expression(expr.object)

        # Convert to tensor if needed
        if isinstance(obj, Truth):
            tensor = obj.value
            semantics = obj.semantics
        elif isinstance(obj, torch.Tensor):
            tensor = obj
            semantics = self.default_semantics
        else:
            raise UnsupportedOperationError(
                f"Indexing operation",
                f"Cannot index object of type {type(obj).__name__}",
            )

        # Process indices
        indices = []
        for index_expr in expr.indices:
            index = self._evaluate_expression(index_expr)

            if isinstance(index, SliceExpression):
                # Convert slice expression to Python slice object
                start = self._evaluate_expression(index.start) if index.start else None
                stop = self._evaluate_expression(index.stop) if index.stop else None
                step = self._evaluate_expression(index.step) if index.step else None

                # Convert to integers if they're floats
                if start is not None:
                    start = int(start) if isinstance(start, (int, float)) else start
                if stop is not None:
                    stop = int(stop) if isinstance(stop, (int, float)) else stop
                if step is not None:
                    step = int(step) if isinstance(step, (int, float)) else step

                indices.append(slice(start, stop, step))

            elif isinstance(index, (int, float)):
                indices.append(int(index))

            elif isinstance(index, torch.Tensor):
                # Handle tensor indices (advanced indexing)
                if index.dtype in [torch.long, torch.int, torch.bool]:
                    indices.append(index)
                else:
                    raise UnsupportedOperationError(
                        f"Indexing operation",
                        f"Index tensor must be integer or boolean, got {index.dtype}",
                    )
            else:
                raise UnsupportedOperationError(
                    f"Indexing operation", f"Invalid index type: {type(index).__name__}"
                )

        # Apply indexing
        try:
            if len(indices) == 1:
                result_tensor = tensor[indices[0]]
            else:
                result_tensor = tensor[tuple(indices)]

            # Return Truth object if original was Truth, otherwise return tensor
            if isinstance(obj, Truth):
                return Truth(result_tensor, semantics)
            else:
                return result_tensor

        except (IndexError, TypeError) as e:
            raise UnsupportedOperationError(
                f"Indexing operation", f"Invalid indexing: {str(e)}"
            )

    def _evaluate_slice_expression(self, expr: SliceExpression) -> SliceExpression:
        """Return the slice expression as-is for processing in index evaluation."""
        return expr

    def _evaluate_function_call(self, expr: FunctionCall) -> Any:
        """Evaluate function calls."""
        if expr.name not in self.builtin_functions:
            available_functions = sorted(self.builtin_functions.keys())
            raise InvalidFunctionError(expr.name, available_functions)

        try:
            args = [self._evaluate_expression(arg) for arg in expr.args]
            return self.builtin_functions[expr.name](*args)
        except TypeError as e:
            # Provide more helpful error message for function call issues
            raise InterpreterError(
                f"Error calling function '{expr.name}': {str(e)}. "
                f"Check the number and types of arguments."
            ) from e

    # Built-in function implementations
    def _sum_function(self, probabilities: TensorTruth, indices: List[int]) -> Truth:
        """Sum probabilities for specified class indices."""
        if not isinstance(indices, list):
            raise TypeMismatchError("list", type(indices).__name__, "indices parameter")

        tensor, semantics = self._prepare_truth_input(probabilities)
        return sum_class_probabilities(
            tensor, indices, semantics=semantics, eps=self.default_eps, dim=-1
        )

    def _exactly_one_function(self, probabilities: TensorTruth) -> Truth:
        """Create exactly-one constraint."""
        tensor, semantics = self._prepare_truth_input(probabilities)
        return exactly_one(tensor, semantics=semantics, eps=self.default_eps, dim=-1)

    def _mutual_exclusion_function(self, *probabilities: TensorTruth) -> Truth:
        """Create mutual exclusion constraint."""
        if len(probabilities) < 2:
            raise InterpreterError("mutual_exclusion requires at least 2 arguments")

        # Convert all arguments to proper format
        processed_probs = []
        semantics = self.default_semantics

        for prob in probabilities:
            if isinstance(prob, Truth):
                processed_probs.append(prob.value)
                semantics = prob.semantics  # Use semantics from Truth objects
            else:
                processed_probs.append(prob)

        return mutual_exclusion(
            *processed_probs, semantics=semantics, eps=self.default_eps
        )

    def _clamp_function(
        self, tensor: TensorTruth, min_val: float = 0.0, max_val: float = 1.0
    ) -> torch.Tensor:
        """Clamp tensor values."""
        # Extract tensor from Truth object if needed
        if isinstance(tensor, Truth):
            tensor = tensor.value
        if not isinstance(tensor, torch.Tensor):
            raise TypeMismatchError("tensor", type(tensor).__name__, "first argument")
        if not isinstance(min_val, (int, float)):
            raise TypeMismatchError(
                "number", type(min_val).__name__, "min_val parameter"
            )
        if not isinstance(max_val, (int, float)):
            raise TypeMismatchError(
                "number", type(max_val).__name__, "max_val parameter"
            )
        if min_val >= max_val:
            raise InterpreterError(
                f"min_val ({min_val}) must be less than max_val ({max_val})"
            )

        return torch.clamp(tensor, min=min_val, max=max_val)

    def _threshold_function(
        self, tensor: TensorTruth, threshold: float = 0.5
    ) -> torch.Tensor:
        """Apply threshold to tensor."""
        # Extract tensor from Truth object if needed
        if isinstance(tensor, Truth):
            tensor = tensor.value
        if not isinstance(tensor, torch.Tensor):
            raise TypeMismatchError("tensor", type(tensor).__name__, "first argument")
        if not isinstance(threshold, (int, float)):
            raise TypeMismatchError(
                "number", type(threshold).__name__, "threshold parameter"
            )

        return (tensor > threshold).float()

    def _at_least_k_function(
        self, probabilities: TensorTruth, k: Union[int, float]
    ) -> Truth:
        """Create at-least-k constraint."""
        # Convert float to int if it's a whole number
        if isinstance(k, float) and k.is_integer():
            k = int(k)

        if not isinstance(k, int) or k < 0:
            raise TypeMismatchError(
                "non-negative integer", type(k).__name__, "k parameter"
            )

        tensor, semantics = self._prepare_truth_input(probabilities)
        return at_least_k(tensor, k, semantics=semantics, eps=self.default_eps, dim=-1)

    def _at_most_k_function(
        self, probabilities: TensorTruth, k: Union[int, float]
    ) -> Truth:
        """Create at-most-k constraint."""
        # Convert float to int if it's a whole number
        if isinstance(k, float) and k.is_integer():
            k = int(k)

        if not isinstance(k, int) or k < 0:
            raise TypeMismatchError(
                "non-negative integer", type(k).__name__, "k parameter"
            )

        tensor, semantics = self._prepare_truth_input(probabilities)
        return at_most_k(tensor, k, semantics=semantics, eps=self.default_eps, dim=-1)

    def _exactly_k_function(
        self, probabilities: TensorTruth, k: Union[int, float]
    ) -> Truth:
        """Create exactly-k constraint."""
        # Convert float to int if it's a whole number
        if isinstance(k, float) and k.is_integer():
            k = int(k)

        if not isinstance(k, int) or k < 0:
            raise TypeMismatchError(
                "non-negative integer", type(k).__name__, "k parameter"
            )

        tensor, semantics = self._prepare_truth_input(probabilities)
        return exactly_k(tensor, k, semantics=semantics, eps=self.default_eps, dim=-1)

    def _threshold_implication_function(
        self,
        antecedent: TensorTruth,
        consequent: TensorTruth,
        threshold: float = 0.5,
    ) -> Truth:
        """Create threshold implication constraint."""
        if not isinstance(threshold, (int, float)):
            raise TypeMismatchError(
                "number", type(threshold).__name__, "threshold parameter"
            )

        # Convert inputs to Truth objects
        antecedent_truth = self._convert_to_truth(antecedent)
        consequent_truth = self._convert_to_truth(consequent)

        return threshold_implication(
            antecedent_truth,
            consequent_truth,
            threshold,
            semantics=antecedent_truth.semantics,
            eps=self.default_eps,
        )

    def _conditional_probability_function(
        self,
        condition: TensorTruth,
        event: TensorTruth,
        target_prob: float,
    ) -> Truth:
        """Create conditional probability constraint."""
        if not isinstance(target_prob, (int, float)):
            raise TypeMismatchError(
                "number", type(target_prob).__name__, "target_prob parameter"
            )
        if not (0.0 <= target_prob <= 1.0):
            raise InterpreterError(
                f"target_prob must be between 0 and 1, got {target_prob}"
            )

        # Convert inputs to Truth objects
        condition_truth = self._convert_to_truth(condition)
        event_truth = self._convert_to_truth(event)

        return conditional_probability(
            condition_truth,
            event_truth,
            target_prob,
            semantics=condition_truth.semantics,
            eps=self.default_eps,
        )

    def _greater_than_function(self, left: TensorTruth, right: TensorTruth) -> Truth:
        """Create greater than comparison."""
        left_truth = self._convert_to_truth(left)
        right_truth = self._convert_to_truth(right)
        return left_truth > right_truth

    def _less_than_function(self, left: TensorTruth, right: TensorTruth) -> Truth:
        """Create less than comparison."""
        left_truth = self._convert_to_truth(left)
        right_truth = self._convert_to_truth(right)
        return left_truth < right_truth

    def _equals_function(self, left: TensorTruth, right: TensorTruth) -> Truth:
        """Create equals comparison."""
        left_truth = self._convert_to_truth(left)
        right_truth = self._convert_to_truth(right)
        return left_truth.eq(right_truth)

    def _threshold_constraint_function(
        self, tensor: TensorTruth, threshold: float, operator: str = ">"
    ) -> Truth:
        """Create threshold constraint with specified operator.

        Args:
            tensor: Input tensor or Truth object
            threshold: Threshold value
            operator: Comparison operator ('>', '<', '==', '>=', '<=')

        Returns:
            Truth object representing the comparison
        """
        if not isinstance(threshold, (int, float)):
            raise TypeMismatchError(
                "number", type(threshold).__name__, "threshold parameter"
            )
        if not isinstance(operator, str):
            raise TypeMismatchError(
                "string", type(operator).__name__, "operator parameter"
            )

        tensor_truth = self._convert_to_truth(tensor)
        threshold_tensor = torch.full_like(
            tensor_truth.value, threshold, device=tensor_truth.value.device
        )
        threshold_truth = Truth(threshold_tensor, tensor_truth.semantics)

        if operator == ">":
            return tensor_truth > threshold_truth
        elif operator == "<":
            return tensor_truth < threshold_truth
        elif operator == "==":
            return tensor_truth.eq(threshold_truth)
        elif operator == ">=":
            return (tensor_truth > threshold_truth) | (tensor_truth.eq(threshold_truth))
        elif operator == "<=":
            return (tensor_truth < threshold_truth) | (tensor_truth.eq(threshold_truth))
        else:
            raise InterpreterError(f"Unknown comparison operator: {operator}")

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable in the interpreter environment."""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """Get a variable from the interpreter environment."""
        if name not in self.variables:
            raise VariableNotFoundError(name)
        return self.variables[name]

    def clear_variables(self) -> None:
        """Clear all variables from the interpreter environment."""
        self.variables.clear()

    def add_builtin_function(self, name: str, func: Callable) -> None:
        """Add a custom built-in function."""
        self.builtin_functions[name] = func

    def _prepare_truth_input(
        self, value: TensorTruth
    ) -> Tuple[torch.Tensor, Semantics]:
        """
        Helper method to extract tensor and semantics from Truth or Tensor input.

        Returns:
            Tuple of (tensor, semantics)
        """
        if isinstance(value, Truth):
            return value.value, value.semantics
        else:
            return value, self.default_semantics

    def _convert_to_truth(self, value: TensorTruth) -> Truth:
        """
        Helper method to convert Tensor or Truth to Truth object.

        Returns:
            Truth object
        """
        if isinstance(value, Truth):
            return value
        else:
            return Truth(_clamp01(value, self.default_eps), self.default_semantics)

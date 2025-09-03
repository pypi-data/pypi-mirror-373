"""
Abstract Syntax Tree (AST) nodes for the logic language.

These classes represent the parsed structure of logic language constructs.
Each node type corresponds to a different language element like expressions,
statements, and operators.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union
from dataclasses import dataclass


class ASTNode(ABC):
    """Base class for all AST nodes."""

    pass


class Expression(ASTNode):
    """Base class for expressions that evaluate to values."""

    pass


class Statement(ASTNode):
    """Base class for statements that perform actions."""

    pass


@dataclass
class Identifier(Expression):
    """Variable identifier (e.g., 'mass_L', 'birads_R')."""

    name: str


@dataclass
class NumberLiteral(Expression):
    """Numeric literal (e.g., 1.0, 0.5)."""

    value: float


@dataclass
class StringLiteral(Expression):
    """String literal (e.g., "logbarrier", "hinge")."""

    value: str


@dataclass
class ListLiteral(Expression):
    """List literal (e.g., [1, 2, 3], [4, 5, 6])."""

    elements: List[Expression]


@dataclass
class BinaryOp(Expression):
    """Binary operation (e.g., A | B, A & B, A >> B)."""

    left: Expression
    operator: str  # '|', '&', '^', '>>'
    right: Expression


@dataclass
class UnaryOp(Expression):
    """Unary operation (e.g., ~A, not A)."""

    operator: str  # '~', 'not'
    operand: Expression


@dataclass
class FunctionCall(Expression):
    """Function call (e.g., sum(birads_L, [4, 5, 6]), exactly_one(birads_R))."""

    name: str
    args: List[Expression]


@dataclass
class IndexExpression(Expression):
    """Indexing operation (e.g., variable[0], tensor[:, 1], data[0:3])."""

    object: Expression  # The object being indexed
    indices: List[
        Expression
    ]  # List of index expressions (supports multi-dimensional indexing)


@dataclass
class SliceExpression(Expression):
    """Slice expression (e.g., 0:3, :, ::2)."""

    start: Optional[Expression] = None
    stop: Optional[Expression] = None
    step: Optional[Expression] = None


@dataclass
class DefineStatement(Statement):
    """Variable definition (e.g., define findings_L = mass_L | mc_L)."""

    name: str
    expression: Expression


@dataclass
class ExpectStatement(Statement):
    """Variable expectation with optional aliasing (e.g., expect left_birads as birads_L, right_birads, mass_L)."""

    variables: List[
        Union[str, tuple]
    ]  # List of variable names or (original_name, alias) tuples


@dataclass
class ConstStatement(Statement):
    """Constant definition (e.g., const threshold = 0.7)."""

    name: str
    value: Union[float, int, str, List[Any]]


@dataclass
class ConstraintStatement(Statement):
    """Constraint declaration with optional parameters."""

    expression: Expression
    weight: Optional[Expression] = None
    transform: Optional[Expression] = None
    params: Optional[dict] = None  # Additional parameters


@dataclass
class CommentStatement(Statement):
    """Comment line (ignored during execution)."""

    text: str


@dataclass
class Program(ASTNode):
    """Root node containing all statements."""

    statements: List[Statement]


# Utility functions for AST construction
def make_binary_op(left: Expression, op: str, right: Expression) -> BinaryOp:
    """Helper to create binary operation nodes."""
    return BinaryOp(left=left, operator=op, right=right)


def make_unary_op(op: str, operand: Expression) -> UnaryOp:
    """Helper to create unary operation nodes."""
    return UnaryOp(operator=op, operand=operand)


def make_function_call(name: str, *args: Expression) -> FunctionCall:
    """Helper to create function call nodes."""
    return FunctionCall(name=name, args=list(args))

"""
Parser for the Logic language.

Implements a     # Token patterns
    TOKEN_PATTERNS = [
        ("COMMENT", r"#.*"),
        ("CONST", r"\bconst\b"),
        ("DEFINE", r"\bdefine\b"),
        ("EXPECT", r"\bexpect\b"),
        ("CONSTRAINT", r"\bconstraint\b"),
        ("WEIGHT", r"\bweight\b"),
        ("TRANSFORM", r"\btransform\b"),
        ("AS", r"\bas\b"),  # Add AS keyword for aliasing
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),descent parser that converts logic scripts into AST.
The grammar supports:
- Variable expectations: expect var1, var2, var3
- Variable definitions: define var_name = expression
-        while not self._at_end() and self._peek().type in [
            "WEIGHT",
            "TRANSFORM",
            "IDENTIFIER",
        ]:
            if self._peek().type == "WEIGHT":
                self._consume("WEIGHT")
                self._consume("EQUALS")
                weight = self._parse_unary()  # Changed to support negative weights
            elif self._peek().type == "TRANSFORM":
                self._consume("TRANSFORM")
                self._consume("EQUALS")
                transform = self._parse_primary()  # Transform is always a string
            else:
                # Custom parameter
                param_name = self._consume("IDENTIFIER").value
                self._consume("EQUALS")
                param_value = self._parse_unary()  # Changed to support negative values
                params[param_name] = param_valueraint expression [weight=value] [transform="type"]
- Expressions: logical operations (|, &, ~, >>), function calls, literals
- Comments: # comment text
"""

import re
from typing import List, Optional, Union, Any
from .ast_nodes import *
from .exceptions import ParseError


class Token:
    """Represents a lexical token."""

    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Lexer:
    """Tokenizes logic language input."""

    # Token patterns
    TOKEN_PATTERNS = [
        ("COMMENT", r"#.*"),
        ("CONST", r"\bconst\b"),
        ("DEFINE", r"\bdefine\b"),
        ("EXPECT", r"\bexpect\b"),
        ("CONSTRAINT", r"\bconstraint\b"),
        ("WEIGHT", r"\bweight\b"),
        ("TRANSFORM", r"\btransform\b"),
        ("AS", r"\bas\b"),  # Add AS keyword for aliasing
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("NUMBER", r"\d+\.?\d*([eE][+-]?\d+)?"),
        ("STRING", r'"[^"]*"|\'[^\']*\''),
        ("IMPLIES", r">>"),
        ("EQ", r"=="),  # Must come before EQUALS
        ("GTE", r">="),  # Greater than or equal
        ("LTE", r"<="),  # Less than or equal
        ("GT", r">"),  # Greater than
        ("LT", r"<"),  # Less than
        ("PIPE", r"\|"),
        ("AMPERSAND", r"&"),
        ("CARET", r"\^"),
        ("TILDE", r"~"),
        ("MINUS", r"-"),  # Minus operator (for negative numbers and subtraction)
        ("PLUS", r"\+"),  # Plus operator (for addition)
        ("MULTIPLY", r"\*"),  # Multiplication operator
        ("DIVIDE", r"/"),  # Division operator
        ("EQUALS", r"="),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACKET", r"\["),
        ("RBRACKET", r"\]"),
        ("COLON", r":"),
        ("COMMA", r","),
        ("SEMICOLON", r";"),
        ("WHITESPACE", r"\s+"),
        ("NEWLINE", r"\n"),
    ]

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        """Convert input text into tokens."""
        while self.pos < len(self.text):
            matched = False

            for token_type, pattern in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.text, self.pos)

                if match:
                    value = match.group(0)

                    if token_type == "NEWLINE":
                        self.line += 1
                        self.column = 1
                        # Include newlines in the token stream for statement separation
                        token = Token(token_type, value, self.line - 1, self.column)
                        self.tokens.append(token)
                    elif token_type != "WHITESPACE":  # Skip whitespace
                        token = Token(token_type, value, self.line, self.column)
                        self.tokens.append(token)

                    self.pos = match.end()
                    if token_type != "NEWLINE":
                        self.column += len(value)
                    matched = True
                    break

            if not matched:
                raise ParseError(
                    f"Unexpected character: '{self.text[self.pos]}'",
                    self.line,
                    self.column,
                )

        return self.tokens


class RuleParser:
    """Recursive descent parser for logic language."""

    def __init__(self):
        self.tokens = []
        self.pos = 0

    def parse(self, text: str) -> Program:
        """Parse rule script text into AST."""
        lexer = Lexer(text)
        self.tokens = lexer.tokenize()
        self.pos = 0

        statements = []
        while not self._at_end():
            # Skip statement separators at the beginning
            self._skip_statement_separators()

            if self._at_end():
                break

            if self._peek().type == "COMMENT":
                statements.append(self._parse_comment())
            elif self._peek().type == "CONST":
                statements.append(self._parse_const())
            elif self._peek().type == "DEFINE":
                statements.append(self._parse_define())
            elif self._peek().type == "EXPECT":
                statements.append(self._parse_expect())
            elif self._peek().type == "CONSTRAINT":
                statements.append(self._parse_constraint())
            else:
                raise ParseError(
                    f"Unexpected token: {self._peek().value}",
                    self._peek().line,
                    self._peek().column,
                )

            # Skip optional statement separators after each statement
            self._skip_statement_separators()

        return Program(statements=statements)

    def _parse_comment(self) -> CommentStatement:
        """Parse comment statement."""
        token = self._consume("COMMENT")
        return CommentStatement(text=token.value[1:].strip())  # Remove '#'

    def _parse_const(self) -> ConstStatement:
        """Parse constant definition."""
        self._consume("CONST")
        name_token = self._consume("IDENTIFIER")
        self._consume("EQUALS")

        # Constants can be any expression that evaluates to a literal value
        value_expr = self._parse_expression()

        # For now, we store the expression and let the interpreter evaluate it
        # The interpreter will ensure it's a constant value
        return ConstStatement(name=name_token.value, value=value_expr)

    def _parse_define(self) -> DefineStatement:
        """Parse variable definition."""
        self._consume("DEFINE")
        name_token = self._consume("IDENTIFIER")
        self._consume("EQUALS")
        expression = self._parse_expression()
        return DefineStatement(name=name_token.value, expression=expression)

    def _parse_expect(self) -> ExpectStatement:
        """Parse variable expectation with optional aliasing."""
        self._consume("EXPECT")

        # Parse comma-separated list of identifiers with optional aliases
        variables = []

        # Parse first variable (required)
        var_name = self._consume("IDENTIFIER").value
        if not self._at_end() and self._peek().type == "AS":
            self._consume("AS")
            alias = self._consume("IDENTIFIER").value
            variables.append((var_name, alias))
        else:
            variables.append(var_name)

        # Parse additional variables
        while not self._at_end() and self._peek().type == "COMMA":
            self._consume("COMMA")
            var_name = self._consume("IDENTIFIER").value
            if not self._at_end() and self._peek().type == "AS":
                self._consume("AS")
                alias = self._consume("IDENTIFIER").value
                variables.append((var_name, alias))
            else:
                variables.append(var_name)

        return ExpectStatement(variables=variables)

    def _parse_constraint(self) -> ConstraintStatement:
        """Parse constraint statement."""
        self._consume("CONSTRAINT")
        expression = self._parse_expression()

        # Parse optional parameters
        weight = None
        transform = None
        params = {}

        while not self._at_end() and self._peek().type in [
            "WEIGHT",
            "TRANSFORM",
            "IDENTIFIER",
        ]:
            if self._peek().type == "WEIGHT":
                self._consume("WEIGHT")
                self._consume("EQUALS")
                weight = self._parse_expression()  # Changed to support expressions
            elif self._peek().type == "TRANSFORM":
                self._consume("TRANSFORM")
                self._consume("EQUALS")
                transform = self._parse_primary()  # Transform is always a string
            else:
                # Handle other named parameters
                param_name = self._consume("IDENTIFIER").value
                self._consume("EQUALS")
                param_value = self._parse_expression()  # Changed to support expressions
                params[param_name] = param_value

        return ConstraintStatement(
            expression=expression,
            weight=weight,
            transform=transform,
            params=params if params else None,
        )

    def _parse_expression(self) -> Expression:
        """Parse expression with operator precedence."""
        return self._parse_implication()

    def _parse_implication(self) -> Expression:
        """Parse implication operator (lowest precedence)."""
        expr = self._parse_or()

        while not self._at_end() and self._peek().type == "IMPLIES":
            op = self._consume("IMPLIES").value
            right = self._parse_or()
            expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_or(self) -> Expression:
        """Parse OR operator."""
        expr = self._parse_xor()

        while not self._at_end() and self._peek().type == "PIPE":
            op = self._consume("PIPE").value
            right = self._parse_xor()
            expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_xor(self) -> Expression:
        """Parse XOR operator."""
        expr = self._parse_comparison()

        while not self._at_end() and self._peek().type == "CARET":
            op = self._consume("CARET").value
            right = self._parse_comparison()
            expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_comparison(self) -> Expression:
        """Parse comparison operators (>, <, ==, >=, <=)."""
        expr = self._parse_and()

        while not self._at_end() and self._peek().type in [
            "GT",
            "LT",
            "EQ",
            "GTE",
            "LTE",
        ]:
            op_token = self._peek()
            if op_token.type == "GT":
                op = self._consume("GT").value
            elif op_token.type == "LT":
                op = self._consume("LT").value
            elif op_token.type == "EQ":
                op = self._consume("EQ").value
            elif op_token.type == "GTE":
                op = self._consume("GTE").value
            elif op_token.type == "LTE":
                op = self._consume("LTE").value

            right = self._parse_and()
            expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_and(self) -> Expression:
        """Parse AND operator."""
        expr = self._parse_arithmetic_term()

        while not self._at_end() and self._peek().type == "AMPERSAND":
            op = self._consume("AMPERSAND").value
            right = self._parse_arithmetic_term()
            expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_arithmetic_term(self) -> Expression:
        """Parse addition and subtraction (lowest arithmetic precedence)."""
        expr = self._parse_arithmetic_factor()

        while not self._at_end() and self._peek().type in ["PLUS", "MINUS"]:
            # Check if this is actually a binary operation (not unary)
            if self._peek().type == "MINUS":
                # Check if this could be a binary minus
                # It's binary if we have a left operand and it's not at the start of an expression
                op = self._consume("MINUS").value
                right = self._parse_arithmetic_factor()
                expr = BinaryOp(left=expr, operator=op, right=right)
            elif self._peek().type == "PLUS":
                op = self._consume("PLUS").value
                right = self._parse_arithmetic_factor()
                expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_arithmetic_factor(self) -> Expression:
        """Parse multiplication and division (higher arithmetic precedence)."""
        expr = self._parse_unary()

        while not self._at_end() and self._peek().type in ["MULTIPLY", "DIVIDE"]:
            if self._peek().type == "MULTIPLY":
                op = self._consume("MULTIPLY").value
            elif self._peek().type == "DIVIDE":
                op = self._consume("DIVIDE").value

            right = self._parse_unary()
            expr = BinaryOp(left=expr, operator=op, right=right)

        return expr

    def _parse_unary(self) -> Expression:
        """Parse unary operators."""
        if not self._at_end() and self._peek().type in [
            "TILDE",
            "AMPERSAND",
            "PIPE",
            "MINUS",
            "PLUS",
        ]:
            op_token = self._peek()
            if op_token.type == "TILDE":  # ~ NOT
                op = self._consume("TILDE").value
            elif op_token.type == "AMPERSAND":  # & AND
                op = self._consume("AMPERSAND").value
            elif op_token.type == "PIPE":  # | OR
                op = self._consume("PIPE").value
            elif op_token.type == "MINUS":  # - NEG
                op = self._consume("MINUS").value
            elif op_token.type == "PLUS":  # + POS
                op = self._consume("PLUS").value

            # Recursively parse unary to handle multiple unary operators (e.g., -(-5))
            operand = self._parse_unary()
            return UnaryOp(operator=op, operand=operand)

        return self._parse_primary()

    def _parse_primary(self) -> Expression:
        """Parse primary expressions."""
        if self._at_end():
            raise ParseError("Unexpected end of input")

        token = self._peek()

        if token.type == "IDENTIFIER":
            name = self._consume("IDENTIFIER").value

            # Check for function call
            if not self._at_end() and self._peek().type == "LPAREN":
                self._consume("LPAREN")
                args = []

                if not self._at_end() and self._peek().type != "RPAREN":
                    args.append(self._parse_expression())

                    while not self._at_end() and self._peek().type == "COMMA":
                        self._consume("COMMA")
                        args.append(self._parse_expression())

                self._consume("RPAREN")
                expr = FunctionCall(name=name, args=args)
            else:
                expr = Identifier(name=name)

            # Check for indexing
            return self._parse_indexing(expr)

        elif token.type == "NUMBER":
            value = float(self._consume("NUMBER").value)
            return NumberLiteral(value=value)

        elif token.type == "STRING":
            value = self._consume("STRING").value[1:-1]  # Remove quotes
            return StringLiteral(value=value)

        elif token.type == "LBRACKET":
            self._consume("LBRACKET")
            elements = []

            if not self._at_end() and self._peek().type != "RBRACKET":
                elements.append(self._parse_expression())

                while not self._at_end() and self._peek().type == "COMMA":
                    self._consume("COMMA")
                    elements.append(self._parse_expression())

            self._consume("RBRACKET")
            return ListLiteral(elements=elements)

        elif token.type == "LPAREN":
            self._consume("LPAREN")
            expr = self._parse_expression()
            self._consume("RPAREN")
            return expr

        else:
            raise ParseError(
                f"Unexpected token: {token.value}", token.line, token.column
            )

    def _parse_indexing(self, expr: Expression) -> Expression:
        """Parse indexing operations like [0], [:, 1], [0:3]."""
        while not self._at_end() and self._peek().type == "LBRACKET":
            self._consume("LBRACKET")
            indices = []

            if not self._at_end() and self._peek().type != "RBRACKET":
                indices.append(self._parse_index_expression())

                while not self._at_end() and self._peek().type == "COMMA":
                    self._consume("COMMA")
                    indices.append(self._parse_index_expression())

            self._consume("RBRACKET")
            expr = IndexExpression(object=expr, indices=indices)

        return expr

    def _parse_index_expression(self) -> Expression:
        """Parse a single index or slice expression."""
        # Check if this is a slice (starts with colon or has colon somewhere)
        if not self._at_end() and self._peek().type == "COLON":
            # Slice starting with colon: [:stop] or [::step]
            self._consume("COLON")

            stop = None
            step = None

            # Check for stop value
            if not self._at_end() and self._peek().type not in [
                "COMMA",
                "RBRACKET",
                "COLON",
            ]:
                stop = self._parse_expression()

            # Check for step
            if not self._at_end() and self._peek().type == "COLON":
                self._consume("COLON")
                if not self._at_end() and self._peek().type not in [
                    "COMMA",
                    "RBRACKET",
                ]:
                    step = self._parse_expression()

            return SliceExpression(start=None, stop=stop, step=step)

        else:
            # Parse the first part (could be start of slice or simple index)
            start_expr = self._parse_expression()

            # Check if this is a slice
            if not self._at_end() and self._peek().type == "COLON":
                self._consume("COLON")

                stop = None
                step = None

                # Check for stop value
                if not self._at_end() and self._peek().type not in [
                    "COMMA",
                    "RBRACKET",
                    "COLON",
                ]:
                    stop = self._parse_expression()

                # Check for step
                if not self._at_end() and self._peek().type == "COLON":
                    self._consume("COLON")
                    if not self._at_end() and self._peek().type not in [
                        "COMMA",
                        "RBRACKET",
                    ]:
                        step = self._parse_expression()

                return SliceExpression(start=start_expr, stop=stop, step=step)

            else:
                # Simple index
                return start_expr

    def _peek(self) -> Token:
        """Look at current token without consuming it."""
        if self._at_end():
            raise ParseError("Unexpected end of input")
        return self.tokens[self.pos]

    def _consume(self, expected_type: str) -> Token:
        """Consume token of expected type."""
        if self._at_end():
            raise ParseError(f"Expected {expected_type}, got end of input")

        token = self.tokens[self.pos]
        if token.type != expected_type:
            raise ParseError(
                f"Expected {expected_type}, got {token.type}", token.line, token.column
            )

        self.pos += 1
        return token

    def _at_end(self) -> bool:
        """Check if we've reached the end of tokens."""
        return self.pos >= len(self.tokens)

    def _skip_statement_separators(self) -> None:
        """Skip newlines and semicolons that separate statements."""
        while not self._at_end() and self._peek().type in ("NEWLINE", "SEMICOLON"):
            self.pos += 1

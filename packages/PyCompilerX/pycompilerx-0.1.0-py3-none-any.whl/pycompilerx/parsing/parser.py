"""
Parser implementation for Python expressions and statements
"""

import ast
import re
from typing import Any, Dict, Union


class PythonParser:
    """A parser for Python expressions and statements."""

    def __init__(self):
        self.tokens = []
        self.current_token = 0

    def parse(self, code: str) -> ast.AST:
        """
        Parse Python code string into AST.

        Args:
            code: Python source code

        Returns:
            AST node representing the parsed code
        """
        try:
            return ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")

    def parse_expression(self, expr: str) -> ast.expr:
        """
        Parse a Python expression.

        Args:
            expr: Python expression as string

        Returns:
            AST expression node
        """
        try:
            return ast.parse(expr, mode='eval').body
        except SyntaxError as e:
            raise ValueError(f"Invalid expression: {e}")

    def parse_statement(self, stmt: str) -> ast.stmt:
        """
        Parse a Python statement.

        Args:
            stmt: Python statement as string

        Returns:
            AST statement node
        """
        try:
            parsed = ast.parse(stmt, mode='exec')
            if len(parsed.body) != 1:
                raise ValueError("Expected exactly one statement")
            return parsed.body[0]
        except SyntaxError as e:
            raise ValueError(f"Invalid statement: {e}")


class SimpleExpressionParser:
    """A simple recursive descent parser for basic arithmetic expressions."""

    def __init__(self):
        self.tokens = []
        self.pos = 0

    def tokenize(self, expr: str):
        """Tokenize a simple arithmetic expression."""
        token_pattern = r'\d+\.?\d*|\+|\-|\*|\/|\(|\)|[a-zA-Z_][a-zA-Z0-9_]*'
        self.tokens = re.findall(token_pattern, expr.replace(' ', ''))
        self.pos = 0

    def current_token(self):
        """Get current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        """Consume current token."""
        token = self.current_token()
        if expected and token != expected:
            raise ValueError(f"Expected {expected}, got {token}")
        self.pos += 1
        return token

    def parse_expression(self, expr: str):
        """Parse arithmetic expression into a simple AST-like structure."""
        self.tokenize(expr)
        return self.parse_term()

    def parse_term(self):
        """Parse term (handles + and -)."""
        left = self.parse_factor()

        while self.current_token() in ['+', '-']:
            op = self.consume()
            right = self.parse_factor()
            left = {'type': 'binop', 'op': op, 'left': left, 'right': right}

        return left

    def parse_factor(self):
        """Parse factor (handles * and /)."""
        left = self.parse_primary()

        while self.current_token() in ['*', '/']:
            op = self.consume()
            right = self.parse_primary()
            left = {'type': 'binop', 'op': op, 'left': left, 'right': right}

        return left

    def parse_primary(self):
        """Parse primary expressions (numbers, variables, parentheses)."""
        token = self.current_token()

        if token and (token.replace('.', '').isdigit()):
            self.consume()
            value = float(token) if '.' in token else int(token)
            return {'type': 'number', 'value': value}
        elif token and (token.isalpha() or token.startswith('_')):
            self.consume()
            return {'type': 'variable', 'name': token}
        elif token == '(':
            self.consume('(')
            expr = self.parse_term()
            self.consume(')')
            return expr
        else:
            raise ValueError(f"Unexpected token: {token}")


def parse_expression(expr: str) -> ast.expr:
    """
    Convenience function to parse a Python expression.

    Args:
        expr: Python expression string

    Returns:
        AST expression node
    """
    parser = PythonParser()
    return parser.parse_expression(expr)


def parse_simple_arithmetic(expr: str) -> Dict[str, Any]:
    """
    Parse simple arithmetic expressions into a dictionary-based AST.

    Args:
        expr: Arithmetic expression (e.g., "2 + 3 * 4")

    Returns:
        Dictionary representing the expression tree
    """
    parser = SimpleExpressionParser()
    return parser.parse_expression(expr)

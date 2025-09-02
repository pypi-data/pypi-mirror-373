"""
AST manipulation tools using Python's built-in ast module
"""

import ast
import sys
from typing import Any, List, Optional, Dict, Union, Tuple


class ASTTransformer(ast.NodeTransformer):
    """Custom AST transformer for code transformations."""

    def __init__(self):
        self.transformations = []

    def visit_BinOp(self, node):
        """Transform binary operations."""
        # Example transformation: optimize constants
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                left_val = node.left.value
                right_val = node.right.value

                if isinstance(node.op, ast.Add):
                    result = left_val + right_val
                elif isinstance(node.op, ast.Sub):
                    result = left_val - right_val
                elif isinstance(node.op, ast.Mult):
                    result = left_val * right_val
                elif isinstance(node.op, ast.Div) and right_val != 0:
                    result = left_val / right_val
                else:
                    return self.generic_visit(node)

                self.transformations.append(f"Constant folding: {left_val} {node.op.__class__.__name__} {right_val} = {result}")
                return ast.Constant(value=result)
            except (TypeError, ZeroDivisionError):
                pass

        return self.generic_visit(node)

    def visit_Name(self, node):
        """Transform variable names."""
        # Example: rename variables starting with 'temp' to start with 'var'
        if isinstance(node.ctx, ast.Store) and node.id.startswith('temp'):
            old_name = node.id
            node.id = node.id.replace('temp', 'var', 1)
            self.transformations.append(f"Renamed variable {old_name} to {node.id}")
        return node


class ASTAnalyzer(ast.NodeVisitor):
    """AST analyzer for code statistics and analysis."""

    def __init__(self):
        self.stats = {
            'functions': 0,
            'classes': 0,
            'variables': set(),
            'imports': [],
            'loops': 0,
            'conditionals': 0,
            'function_calls': 0
        }

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        self.stats['functions'] += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.stats['classes'] += 1
        self.generic_visit(node)

    def visit_Name(self, node):
        """Visit variable names."""
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            self.stats['variables'].add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.stats['imports'].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from-import statements."""
        module = node.module or ""
        for alias in node.names:
            self.stats['imports'].append(f"{module}.{alias.name}")
        self.generic_visit(node)

    def visit_For(self, node):
        """Visit for loops."""
        self.stats['loops'] += 1
        self.generic_visit(node)

    def visit_While(self, node):
        """Visit while loops."""
        self.stats['loops'] += 1
        self.generic_visit(node)

    def visit_If(self, node):
        """Visit if statements."""
        self.stats['conditionals'] += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        """Visit function calls."""
        self.stats['function_calls'] += 1
        self.generic_visit(node)


def parse_code(code: str) -> ast.AST:
    """
    Parse Python code string into AST.

    Args:
        code: Python source code

    Returns:
        AST representation of the code
    """
    try:
        return ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")


def ast_to_string(tree: ast.AST) -> str:
    """
    Convert AST back to Python code string.

    Args:
        tree: AST node

    Returns:
        Python source code as string
    """
    try:
        # Use ast.unparse if available (Python 3.9+)
        if hasattr(ast, 'unparse'):
            return ast.unparse(tree)
        else:
            # Fallback for older Python versions
            return f"<AST conversion requires Python 3.9+ (current: {sys.version_info})>"
    except Exception as e:
        return f"<Error converting AST to string: {e}>"


def analyze_code(code: str) -> Dict[str, Any]:
    """
    Analyze Python code and return statistics.

    Args:
        code: Python source code

    Returns:
        Dictionary containing code analysis results
    """
    tree = parse_code(code)
    analyzer = ASTAnalyzer()
    analyzer.visit(tree)

    # Convert set to list for JSON serialization
    stats = analyzer.stats.copy()
    stats['variables'] = list(stats['variables'])

    return stats


def transform_code(code: str, transformer_class=ASTTransformer) -> Tuple[str, List[str]]:
    """
    Transform Python code using a custom transformer.

    Args:
        code: Python source code
        transformer_class: AST transformer class to use

    Returns:
        Tuple of (transformed_code, list_of_transformations)
    """
    tree = parse_code(code)
    transformer = transformer_class()
    transformed_tree = transformer.visit(tree)

    # Fix missing locations
    ast.fix_missing_locations(transformed_tree)

    transformed_code = ast_to_string(transformed_tree)
    return transformed_code, transformer.transformations


def pretty_print_ast(tree: ast.AST, indent: int = 0) -> str:
    """
    Pretty print AST structure for debugging.

    Args:
        tree: AST node
        indent: Current indentation level

    Returns:
        String representation of AST structure
    """
    result = []
    prefix = "  " * indent

    if isinstance(tree, ast.AST):
        result.append(f"{prefix}{tree.__class__.__name__}")
        for field, value in ast.iter_fields(tree):
            result.append(f"{prefix}  {field}:")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        result.append(pretty_print_ast(item, indent + 2))
                    else:
                        result.append(f"{prefix}    {repr(item)}")
            elif isinstance(value, ast.AST):
                result.append(pretty_print_ast(value, indent + 2))
            else:
                result.append(f"{prefix}    {repr(value)}")
    else:
        result.append(f"{prefix}{repr(tree)}")

    return "\n".join(result)


def find_functions(code: str) -> List[Dict[str, Any]]:
    """
    Find all function definitions in code.

    Args:
        code: Python source code

    Returns:
        List of function information dictionaries
    """
    tree = parse_code(code)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'line': getattr(node, 'lineno', 0),
                'docstring': ast.get_docstring(node)
            }
            functions.append(func_info)

    return functions


def validate_syntax(code: str) -> Dict[str, Any]:
    """
    Validate Python code syntax.

    Args:
        code: Python source code

    Returns:
        Dictionary with validation results
    """
    try:
        ast.parse(code)
        return {
            'valid': True,
            'message': 'Syntax is valid',
            'error': None
        }
    except SyntaxError as e:
        return {
            'valid': False,
            'message': f'Syntax error at line {e.lineno}: {e.msg}',
            'error': str(e)
        }

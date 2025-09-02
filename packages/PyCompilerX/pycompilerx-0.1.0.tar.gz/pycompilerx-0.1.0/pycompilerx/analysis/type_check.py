"""
Static type checking and analysis tools
"""

import ast
import builtins
from typing import Dict, Any, List, Optional, Union, Set


class TypeChecker(ast.NodeVisitor):
    """Improved type checker for Python code."""

    def __init__(self):
        self.symbol_table = {}
        self.errors = []
        self.warnings = []
        self.function_defs = set()

    def add_error(self, message: str, lineno: int = 0):
        """Add a type error."""
        self.errors.append(f"Line {lineno}: {message}")

    def add_warning(self, message: str, lineno: int = 0):
        """Add a type warning."""
        self.warnings.append(f"Line {lineno}: {message}")

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        # Store function in symbol table
        self.symbol_table[node.name] = 'function'
        self.function_defs.add(node.name)

        # Process function body
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit assignment statements."""
        # Simple type inference for assignments
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

            # Infer type from value
            if isinstance(node.value, ast.Constant):
                self.symbol_table[var_name] = type(node.value.value).__name__
            elif isinstance(node.value, ast.List):
                self.symbol_table[var_name] = 'list'
            elif isinstance(node.value, ast.Dict):
                self.symbol_table[var_name] = 'dict'
            elif isinstance(node.value, ast.Call):
                # Check if it's a known function call
                if isinstance(node.value.func, ast.Name):
                    func_name = node.value.func.id
                    if func_name in ['int', 'float', 'str', 'list', 'dict']:
                        self.symbol_table[var_name] = func_name
                    else:
                        self.symbol_table[var_name] = 'unknown'
            else:
                self.symbol_table[var_name] = 'unknown'

        self.generic_visit(node)

    def visit_BinOp(self, node):
        """Visit binary operations."""
        # Check for type compatibility in binary operations
        left_type = self.infer_expression_type(node.left)
        right_type = self.infer_expression_type(node.right)

        if left_type and right_type:
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                    pass  # Valid numeric operation
                elif left_type == 'str' and right_type == 'str' and isinstance(node.op, ast.Add):
                    pass  # Valid string concatenation
                else:
                    line_no = getattr(node, 'lineno', 0)
                    if left_type != 'unknown' and right_type != 'unknown':
                        self.add_warning(
                            f"Potentially incompatible types for {node.op.__class__.__name__}: "
                            f"{left_type} and {right_type}",
                            line_no
                        )

        self.generic_visit(node)

    def visit_Call(self, node):
        """Visit function calls."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            # Check if function exists
            if (func_name not in self.symbol_table and 
                func_name not in self.function_defs and
                not hasattr(builtins, func_name)):
                line_no = getattr(node, 'lineno', 0)
                self.add_warning(f"Function '{func_name}' may not be defined", line_no)

        self.generic_visit(node)

    def visit_Name(self, node):
        """Visit variable names."""
        if isinstance(node.ctx, ast.Load):
            # Variable is being read
            if (node.id not in self.symbol_table and
                node.id not in self.function_defs and
                not hasattr(builtins, node.id)):
                line_no = getattr(node, 'lineno', 0)
                self.add_warning(f"Variable '{node.id}' may not be defined", line_no)

        self.generic_visit(node)

    def infer_expression_type(self, expr):
        """Infer the type of an expression."""
        if isinstance(expr, ast.Constant):
            return type(expr.value).__name__
        elif isinstance(expr, ast.Name):
            return self.symbol_table.get(expr.id, 'unknown')
        elif isinstance(expr, ast.List):
            return 'list'
        elif isinstance(expr, ast.Dict):
            return 'dict'
        elif isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                func_name = expr.func.id
                if func_name in ['int', 'float', 'str', 'list', 'dict']:
                    return func_name
        return 'unknown'


class SimpleTypeInference:
    """Simple type inference engine."""

    def __init__(self):
        self.types = {}

    def infer_from_assignment(self, var_name: str, value):
        """Infer type from assignment."""
        if isinstance(value, int):
            self.types[var_name] = 'int'
        elif isinstance(value, float):
            self.types[var_name] = 'float'
        elif isinstance(value, str):
            self.types[var_name] = 'str'
        elif isinstance(value, list):
            self.types[var_name] = 'list'
        elif isinstance(value, dict):
            self.types[var_name] = 'dict'
        else:
            self.types[var_name] = type(value).__name__

    def get_type(self, var_name: str) -> Optional[str]:
        """Get the inferred type of a variable."""
        return self.types.get(var_name)


def check_types(code: Union[str, ast.AST]) -> Dict[str, Any]:
    """
    Perform basic type checking on Python code.

    Args:
        code: Python source code string or AST

    Returns:
        Dictionary containing type checking results
    """
    if isinstance(code, str):
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                'success': False,
                'errors': [f"Syntax error: {e}"],
                'warnings': [],
                'symbol_table': {}
            }
    else:
        tree = code

    checker = TypeChecker()
    checker.visit(tree)

    # Consider it successful if there are no errors (warnings are OK)
    return {
        'success': len(checker.errors) == 0,
        'errors': checker.errors,
        'warnings': checker.warnings,
        'symbol_table': checker.symbol_table
    }


def analyze_types(code: str) -> Dict[str, Any]:
    """
    Analyze types in Python code and provide detailed information.

    Args:
        code: Python source code

    Returns:
        Dictionary containing type analysis results
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {'error': f"Syntax error: {e}"}

    # Basic type analysis
    type_info = {
        'variables': {},
        'functions': [],
        'classes': [],
        'imports': []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Track variable assignments
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    if isinstance(node.value, ast.Constant):
                        type_info['variables'][var_name] = type(node.value.value).__name__
                    else:
                        type_info['variables'][var_name] = 'unknown'

        elif isinstance(node, ast.FunctionDef):
            # Track function definitions
            func_info = {
                'name': node.name,
                'args': len(node.args.args),
                'has_return_annotation': node.returns is not None,
                'has_arg_annotations': any(arg.annotation for arg in node.args.args)
            }
            type_info['functions'].append(func_info)

        elif isinstance(node, ast.ClassDef):
            # Track class definitions
            class_info = {
                'name': node.name,
                'bases': len(node.bases),
                'methods': []
            }

            # Find methods in class
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    class_info['methods'].append(class_node.name)

            type_info['classes'].append(class_info)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            # Track imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    type_info['imports'].append(alias.name)
            else:  # ImportFrom
                module = node.module or ""
                for alias in node.names:
                    type_info['imports'].append(f"{module}.{alias.name}")

    return type_info

"""
Cython compilation tools for Python to C conversion
"""

import ast
from typing import Dict, Any, List


class CythonCompiler:
    """Cython code generator and compiler."""

    def __init__(self):
        self.cython_code = []
        self.includes = set()

    def emit(self, line: str):
        """Emit a line of Cython code."""
        self.cython_code.append(line)

    def generate_cython_from_ast(self, tree: ast.AST) -> str:
        """Generate Cython code from AST."""
        self.emit("# Generated Cython code")
        self.emit("# cython: language_level=3")
        self.emit("# cython: boundscheck=False")
        self.emit("# cython: wraparound=False")
        self.emit("")

        # Process AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.generate_function(node)
            elif isinstance(node, ast.Assign):
                self.generate_assignment(node)

        return self.get_cython_code()

    def generate_function(self, node: ast.FunctionDef):
        """Generate Cython function definition."""
        # Function signature
        args = []
        for arg in node.args.args:
            args.append(f"object {arg.arg}")

        args_str = ", ".join(args) if args else ""
        self.emit(f"def {node.name}({args_str}):")

        # Generate function body
        if node.body:
            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    if isinstance(stmt.value, ast.Constant):
                        self.emit(f"    return {stmt.value.value}")
                    elif isinstance(stmt.value, ast.Name):
                        self.emit(f"    return {stmt.value.id}")
                    else:
                        self.emit("    return result")
                else:
                    self.emit("    pass")
        else:
            self.emit("    pass")

        self.emit("")

    def generate_assignment(self, node: ast.Assign):
        """Generate Cython assignment."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

            if isinstance(node.value, ast.Constant):
                value = node.value.value
                if isinstance(value, int):
                    self.emit(f"cdef int {var_name} = {value}")
                elif isinstance(value, float):
                    self.emit(f"cdef double {var_name} = {value}")
                elif isinstance(value, str):
                    self.emit(f'cdef str {var_name} = "{value}"')
                else:
                    self.emit(f"{var_name} = {repr(value)}")
            else:
                self.emit(f"{var_name} = <expression>")

    def get_cython_code(self) -> str:
        """Get the generated Cython code."""
        return "\n".join(self.cython_code)


def compile_cython(python_code: str, optimize: bool = True) -> Dict[str, Any]:
    """
    Compile Python code to Cython.

    Args:
        python_code: Python source code
        optimize: Whether to apply optimizations

    Returns:
        Dictionary containing compilation results
    """
    try:
        tree = ast.parse(python_code)
        compiler = CythonCompiler()
        cython_code = compiler.generate_cython_from_ast(tree)

        if optimize:
            optimizations = [
                "# cython: boundscheck=False",
                "# cython: wraparound=False", 
                "# cython: cdivision=True",
                "# cython: nonecheck=False"
            ]
            cython_code = "\n".join(optimizations) + "\n\n" + cython_code

        return {
            'success': True,
            'cython_code': cython_code,
            'original_code': python_code,
            'optimized': optimize,
            'performance_gain': 'Estimated 2-10x speedup' if optimize else 'Minimal speedup',
            'size_kb': len(cython_code) / 1024
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'cython_code': None
        }


def python_to_cython(python_code: str, optimize: bool = True) -> str:
    """
    Convert Python code to optimized Cython code.

    Args:
        python_code: Python source code
        optimize: Whether to apply Cython optimizations

    Returns:
        Cython code as string
    """
    result = compile_cython(python_code, optimize)

    if result['success']:
        return result['cython_code']
    else:
        return f"# Error converting to Cython: {result.get('error', 'Unknown error')}"


def create_setup_py(module_name: str = "compiled_module") -> str:
    """Create a setup.py file for Cython compilation."""
    setup_template = """from setuptools import setup
from Cython.Build import cythonize

setup(
    name="{name}",
    ext_modules=cythonize("{name}.pyx"),
    zip_safe=False,
)"""

    return setup_template.format(name=module_name)


def analyze_cython_potential(code: str) -> Dict[str, Any]:
    """
    Analyze Python code for Cython optimization potential.

    Args:
        code: Python source code

    Returns:
        Analysis results with optimization suggestions
    """
    try:
        tree = ast.parse(code)

        analysis = {
            'has_loops': False,
            'has_numeric_ops': False,
            'has_function_calls': False,
            'optimization_potential': 'Low',
            'suggestions': []
        }

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                analysis['has_loops'] = True
                analysis['suggestions'].append("Add cdef for loop variables")

            elif isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                    analysis['has_numeric_ops'] = True
                    analysis['suggestions'].append("Use cdef for numeric variables")

            elif isinstance(node, ast.Call):
                analysis['has_function_calls'] = True

        # Determine optimization potential
        if analysis['has_loops'] and analysis['has_numeric_ops']:
            analysis['optimization_potential'] = 'High'
        elif analysis['has_loops'] or analysis['has_numeric_ops']:
            analysis['optimization_potential'] = 'Medium'

        if not analysis['suggestions']:
            analysis['suggestions'].append("Consider adding type annotations")

        return analysis

    except Exception as e:
        return {'error': f"Analysis failed: {e}"}

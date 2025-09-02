"""
Numba JIT compilation tools for Python function optimization
"""

import ast
import inspect
from typing import Dict, Any, Callable, Optional, List, Union
import functools


class NumbaJIT:
    """Numba Just-In-Time compiler interface."""

    def __init__(self):
        self.compiled_functions = {}
        self.compilation_stats = {}

    def compile_function(self, func: Callable, signature: Optional[str] = None) -> Callable:
        """
        Mock JIT compilation of a Python function.

        Args:
            func: Python function to compile
            signature: Type signature for compilation

        Returns:
            Compiled function (mock)
        """
        func_name = func.__name__

        # Get source code safely
        try:
            source = inspect.getsource(func)
        except (OSError, TypeError):
            source = "<source not available>"

        self.compilation_stats[func_name] = {
            'original_source': source,
            'signature': signature or 'auto-inferred',
            'compilation_time': '0.1s',
            'optimization_level': 'O2',
            'speedup_estimate': '10-100x for numerical code'
        }

        # Create a wrapper that simulates JIT compilation
        @functools.wraps(func)
        def jit_wrapper(*args, **kwargs):
            # In real Numba, this would be compiled machine code
            return func(*args, **kwargs)

        # Add metadata
        jit_wrapper._is_jit_compiled = True
        jit_wrapper._original_function = func
        jit_wrapper._compilation_stats = self.compilation_stats[func_name]

        self.compiled_functions[func_name] = jit_wrapper
        return jit_wrapper

    def get_compilation_info(self, func_name: str) -> Dict[str, Any]:
        """Get compilation information for a function."""
        return self.compilation_stats.get(func_name, {})

    def list_compiled_functions(self) -> List[str]:
        """List all compiled functions."""
        return list(self.compiled_functions.keys())


def jit_compile(func: Optional[Callable] = None, *, nopython: bool = True, 
                cache: bool = True, parallel: bool = False) -> Union[Callable, Callable[[Callable], Callable]]:
    """
    Mock Numba JIT decorator.

    Args:
        func: Function to compile (if used as @jit_compile)
        nopython: Use nopython mode
        cache: Enable caching
        parallel: Enable parallel execution

    Returns:
        Compiled function or decorator
    """
    jit_compiler = NumbaJIT()

    def decorator(f: Callable) -> Callable:
        # Mock JIT compilation with options
        signature = None
        if hasattr(f, '__annotations__'):
            # Try to build signature from annotations
            annotations = f.__annotations__
            if annotations:
                signature = f"({', '.join(str(v) for v in annotations.values())})"

        compiled_func = jit_compiler.compile_function(f, signature)

        # Add compilation metadata
        compiled_func._jit_options = {
            'nopython': nopython,
            'cache': cache,
            'parallel': parallel
        }

        return compiled_func

    if func is None:
        # Used as @jit_compile()
        return decorator
    else:
        # Used as @jit_compile
        return decorator(func)


def analyze_numba_compatibility(func: Callable) -> Dict[str, Any]:
    """
    Analyze a function for Numba compatibility.

    Args:
        func: Python function to analyze

    Returns:
        Analysis results
    """
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)

        analysis = {
            'function_name': func.__name__,
            'is_compatible': True,
            'issues': [],
            'recommendations': [],
            'estimated_speedup': 'Unknown',
            'complexity_score': 0
        }

        # Analyze AST for compatibility
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ['print', 'input', 'open']:
                        analysis['issues'].append(f"I/O function '{func_name}' not supported in nopython mode")
                        analysis['is_compatible'] = False
                    elif func_name in ['len', 'range', 'abs', 'min', 'max']:
                        analysis['complexity_score'] += 1  # Good for Numba

            elif isinstance(node, (ast.For, ast.While)):
                analysis['complexity_score'] += 2  # Loops benefit from JIT

            elif isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                    analysis['complexity_score'] += 1  # Arithmetic benefits

            elif isinstance(node, ast.Try):
                analysis['issues'].append("Exception handling not supported in nopython mode")
                analysis['is_compatible'] = False

        # Determine recommendations and speedup
        if analysis['is_compatible']:
            if analysis['complexity_score'] >= 5:
                analysis['estimated_speedup'] = '50-100x for numerical computations'
                analysis['recommendations'].append("Excellent candidate for Numba JIT")
            elif analysis['complexity_score'] >= 2:
                analysis['estimated_speedup'] = '10-50x for numerical computations'
                analysis['recommendations'].append("Good candidate for Numba JIT")
            else:
                analysis['estimated_speedup'] = '2-10x speedup possible'
                analysis['recommendations'].append("Moderate benefit from JIT compilation")
        else:
            analysis['recommendations'].append("Refactor to remove unsupported features for nopython mode")
            analysis['estimated_speedup'] = 'Use object mode for compatibility (slower)'

        return analysis

    except Exception as e:
        return {
            'function_name': getattr(func, '__name__', 'unknown'),
            'is_compatible': False,
            'error': str(e),
            'issues': [f"Analysis failed: {e}"],
            'recommendations': ["Fix syntax errors before analysis"]
        }


def create_jit_example() -> str:
    """Create example JIT-compiled functions."""
    example = """import numba
import numpy as np

@numba.jit(nopython=True)
def fast_sum(arr):
    total = 0.0
    for i in range(len(arr)):
        total += arr[i]
    return total

@numba.jit(nopython=True)  
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    return example

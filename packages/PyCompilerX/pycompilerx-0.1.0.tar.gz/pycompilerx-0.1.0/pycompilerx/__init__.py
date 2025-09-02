"""
PyCompilerX - A Comprehensive Python Compiler Toolkit

This package provides tools and utilities for creating, manipulating, and compiling Python code.
"""

__version__ = "0.1.0"
__author__ = "PyCompilerX Team" 
__email__ = "contact@pycompilerx.dev"

# Import main modules for easy access
try:
    from . import parsing
    from . import analysis
    from . import backend
    from . import examples

    # Convenience imports
    from .parsing.ast_tools import parse_code, ast_to_string, analyze_code
    from .analysis.type_check import check_types, analyze_types
    from .backend.llvm import generate_llvm_ir
    from .backend.cython import compile_cython
    from .backend.numba import jit_compile
    from .examples.basic_calc import BasicCalculator, evaluate_expression

    __all__ = [
        'parsing', 'analysis', 'backend', 'examples',
        'parse_code', 'ast_to_string', 'analyze_code',
        'check_types', 'analyze_types', 'generate_llvm_ir',
        'compile_cython', 'jit_compile', 'BasicCalculator', 'evaluate_expression'
    ]

except ImportError as e:
    # Handle import errors gracefully during development
    print(f"Warning: Some PyCompilerX modules could not be imported: {e}")
    __all__ = []

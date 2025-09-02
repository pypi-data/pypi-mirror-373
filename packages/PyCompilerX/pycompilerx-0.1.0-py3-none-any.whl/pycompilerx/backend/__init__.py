"""
Backend module for PyCompilerX

Provides code generation and compilation tools.
"""

from .llvm import LLVMCodeGenerator, generate_llvm_ir, compile_to_llvm
from .cython import CythonCompiler, compile_cython, python_to_cython
from .numba import NumbaJIT, jit_compile, analyze_numba_compatibility

__all__ = [
    "LLVMCodeGenerator", "generate_llvm_ir", "compile_to_llvm",
    "CythonCompiler", "compile_cython", "python_to_cython",
    "NumbaJIT", "jit_compile", "analyze_numba_compatibility"
]

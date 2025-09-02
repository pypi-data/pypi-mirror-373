"""
Analysis module for PyCompilerX

Provides static analysis and type checking tools.
"""

from .type_check import TypeChecker, check_types, analyze_types, SimpleTypeInference

__all__ = ["TypeChecker", "check_types", "analyze_types", "SimpleTypeInference"]

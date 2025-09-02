"""
Comprehensive tests for PyCompilerX functionality
"""

import pytest
import ast
from pycompilerx import parse_code, check_types, BasicCalculator
from pycompilerx.parsing.lexer import PythonLexer, quick_tokenize
from pycompilerx.parsing.parser import PythonParser, parse_simple_arithmetic
from pycompilerx.parsing.ast_tools import analyze_code, transform_code, validate_syntax
from pycompilerx.analysis.type_check import TypeChecker, analyze_types
from pycompilerx.backend.llvm import generate_llvm_ir, compile_to_llvm
from pycompilerx.backend.cython import compile_cython, analyze_cython_potential
from pycompilerx.backend.numba import jit_compile, analyze_numba_compatibility
from pycompilerx.examples.ast_transform import OptimizingTransformer


class TestParsing:
    """Test parsing functionality."""

    def test_parse_simple_code(self):
        """Test parsing simple Python code."""
        code = "x = 5 + 3"
        tree = parse_code(code)
        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_parse_function(self):
        """Test parsing function definition."""
        code = """
def test_function(x: int, y: int) -> int:
    return x + y
"""
        tree = parse_code(code)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.FunctionDef)

    def test_lexer(self):
        """Test lexical analysis."""
        lexer = PythonLexer()
        tokens = lexer.tokenize_string("x = 42")
        assert len(tokens) > 0
        assert any(token[1] == 'x' for token in tokens)
        assert any(token[1] == '42' for token in tokens)

    def test_quick_tokenize(self):
        """Test quick tokenization."""
        tokens = quick_tokenize("print('hello')")
        assert len(tokens) > 0
        token_strings = [token[1] for token in tokens]
        assert 'print' in token_strings

    def test_validate_syntax(self):
        """Test syntax validation."""
        valid_code = "x = 5"
        invalid_code = "x = 5 +"

        result_valid = validate_syntax(valid_code)
        result_invalid = validate_syntax(invalid_code)

        assert result_valid['valid'] is True
        assert result_invalid['valid'] is False

    def test_simple_arithmetic_parser(self):
        """Test simple arithmetic parser."""
        result = parse_simple_arithmetic("2 + 3 * 4")
        assert result is not None
        assert result['type'] == 'binop'


class TestAnalysis:
    """Test analysis functionality."""

    def test_analyze_code(self):
        """Test code analysis."""
        code = """
def test_function(x, y):
    z = x + y
    return z

class TestClass:
    def method(self):
        pass

import os
from math import sqrt
"""
        analysis = analyze_code(code)
        assert analysis['functions'] == 2  # test_function and method
        assert analysis['classes'] == 1
        assert 'z' in analysis['variables']
        assert len(analysis['imports']) >= 2

    def test_type_checking_success(self):
        """Test successful type checking."""
        code = """
x = 5
y = 10
z = x + y
"""
        result = check_types(code)
        assert result['success'] is True
        assert 'x' in result['symbol_table']
        assert result['symbol_table']['x'] == 'int'

    def test_type_checking_with_function(self):
        """Test type checking with function definition."""
        code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
"""
        result = check_types(code)
        # Should succeed (no errors, warnings are OK)
        assert len(result['errors']) == 0
        assert 'add_numbers' in result['symbol_table']

    def test_analyze_types(self):
        """Test detailed type analysis."""
        code = """
def calculator(x: int, y: int) -> int:
    return x + y

class MathHelper:
    def multiply(self, a, b):
        return a * b

result = calculator(5, 3)
"""
        analysis = analyze_types(code)
        assert len(analysis['functions']) == 2
        assert len(analysis['classes']) == 1
        assert analysis['functions'][0]['has_return_annotation'] is True
        assert analysis['functions'][0]['has_arg_annotations'] is True


class TestBackend:
    """Test backend functionality."""

    def test_llvm_ir_generation(self):
        """Test LLVM IR generation."""
        code = "x = 42"
        ir = generate_llvm_ir(code)
        assert "; Generated LLVM IR" in ir
        assert "define i32 @main()" in ir

    def test_compile_to_llvm(self):
        """Test compiling simple expression to LLVM."""
        ir = compile_to_llvm("x = 5")
        assert "target triple" in ir
        assert "define i32 @main()" in ir

    def test_cython_compilation(self):
        """Test Cython compilation."""
        code = """
def fast_function(x):
    return x * 2
"""
        result = compile_cython(code)
        assert result['success'] is True
        assert "def fast_function" in result['cython_code']
        assert result['performance_gain'] is not None

    def test_cython_analysis(self):
        """Test Cython potential analysis."""
        code = """
def compute_sum(data):
    total = 0
    for item in data:
        total += item * 2
    return total
"""
        analysis = analyze_cython_potential(code)
        assert analysis['has_loops'] is True
        assert analysis['has_numeric_ops'] is True
        assert analysis['optimization_potential'] == 'High'

    def test_numba_jit_compile(self):
        """Test Numba JIT compilation (mock)."""
        @jit_compile
        def test_function(x):
            return x * 2

        assert hasattr(test_function, '_is_jit_compiled')
        assert test_function._is_jit_compiled is True
        assert test_function(5) == 10  # Function should still work

    def test_numba_compatibility_analysis(self):
        """Test Numba compatibility analysis."""
        def numeric_function(x, y):
            result = 0
            for i in range(x):
                result += i * y
            return result

        analysis = analyze_numba_compatibility(numeric_function)
        assert analysis['function_name'] == 'numeric_function'
        assert analysis['complexity_score'] > 0
        assert len(analysis['recommendations']) > 0


class TestExamples:
    """Test example functionality."""

    def test_basic_calculator(self):
        """Test basic calculator functionality."""
        calc = BasicCalculator()

        # Test simple arithmetic
        assert calc.evaluate_expression("2 + 3") == 5
        assert calc.evaluate_expression("10 - 4") == 6
        assert calc.evaluate_expression("3 * 4") == 12
        assert calc.evaluate_expression("15 / 3") == 5.0
        assert calc.evaluate_expression("2 ** 3") == 8
        assert calc.evaluate_expression("10 % 3") == 1

    def test_calculator_with_parentheses(self):
        """Test calculator with complex expressions."""
        calc = BasicCalculator()

        assert calc.evaluate_expression("(2 + 3) * 4") == 20
        assert calc.evaluate_expression("2 * (3 + 4)") == 14
        assert calc.evaluate_expression("(10 - 5) / (2 + 3)") == 1.0

    def test_calculator_with_variables(self):
        """Test calculator with variables."""
        calc = BasicCalculator()

        calc.set_variable("x", 10)
        calc.set_variable("y", 5)

        assert calc.evaluate_expression("x + y") == 15
        assert calc.evaluate_expression("x * y") == 50
        assert calc.evaluate_expression("x / y") == 2.0

    def test_calculator_script_evaluation(self):
        """Test calculator script evaluation."""
        calc = BasicCalculator()

        script = """
        a = 5
        b = 3
        c = a * b
        result = c + 10
        """

        final_result = calc.evaluate_script(script)
        assert final_result == 25  # (5 * 3) + 10
        assert calc.get_variable('result') == 25

    def test_calculator_error_handling(self):
        """Test calculator error handling."""
        calc = BasicCalculator()

        with pytest.raises(ValueError):
            calc.evaluate_expression("10 / 0")  # Division by zero

        with pytest.raises(ValueError):
            calc.evaluate_expression("undefined_var + 5")  # Undefined variable

    def test_ast_transformation(self):
        """Test AST transformations."""
        code = "result = 5 + 3 * 2"
        transformed, transformations = transform_code(code, OptimizingTransformer)

        # Should have applied constant folding
        assert len(transformations) > 0
        assert any("Constant folding" in t for t in transformations)


class TestIntegration:
    """Integration tests."""

    def test_full_pipeline(self):
        """Test complete processing pipeline."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(5)
"""

        # Parse
        tree = parse_code(code)
        assert tree is not None

        # Analyze
        analysis = analyze_code(code)
        assert analysis['functions'] == 1
        assert 'result' in analysis['variables']

        # Type check
        type_result = check_types(code)
        assert len(type_result['errors']) == 0  # Should have no errors

        # Generate LLVM
        llvm_ir = generate_llvm_ir(code)
        assert "define i32 @main()" in llvm_ir

        # Compile Cython
        cython_result = compile_cython(code)
        assert cython_result['success'] is True

    def test_error_resilience(self):
        """Test error handling across modules."""
        invalid_code = "def incomplete_function("

        # Should handle syntax errors gracefully
        syntax_result = validate_syntax(invalid_code)
        assert syntax_result['valid'] is False

        type_result = check_types(invalid_code)
        assert type_result['success'] is False
        assert len(type_result['errors']) > 0


def test_imports():
    """Test that all imports work correctly."""
    # Test main package import
    import pycompilerx
    assert hasattr(pycompilerx, '__version__')

    # Test submodule imports
    from pycompilerx import parsing, analysis, backend, examples
    assert parsing is not None
    assert analysis is not None
    assert backend is not None
    assert examples is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

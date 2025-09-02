"""
AST transformation examples demonstrating code manipulation
"""

import ast
from typing import List, Dict, Any, Optional
from ..parsing.ast_tools import (
    parse_code, ast_to_string, ASTTransformer, 
    transform_code, analyze_code, pretty_print_ast
)
from ..analysis.type_check import check_types


class OptimizingTransformer(ASTTransformer):
    """AST transformer that applies common optimizations."""

    def visit_BinOp(self, node):
        """Optimize binary operations."""
        # Constant folding
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            left_val = node.left.value
            right_val = node.right.value

            try:
                if isinstance(node.op, ast.Add):
                    result = left_val + right_val
                elif isinstance(node.op, ast.Sub):
                    result = left_val - right_val
                elif isinstance(node.op, ast.Mult):
                    result = left_val * right_val
                elif isinstance(node.op, ast.Div):
                    if right_val != 0:
                        result = left_val / right_val
                    else:
                        return self.generic_visit(node)  # Don't optimize division by zero
                else:
                    return self.generic_visit(node)

                # Replace with constant
                self.transformations.append(
                    f"Constant folding: {left_val} {type(node.op).__name__} {right_val} = {result}"
                )
                return ast.Constant(value=result)

            except (TypeError, ZeroDivisionError):
                pass

        # Identity optimizations
        if isinstance(node.op, ast.Add):
            # x + 0 = x
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                self.transformations.append("Removed addition of zero")
                return node.left
            # 0 + x = x  
            elif isinstance(node.left, ast.Constant) and node.left.value == 0:
                self.transformations.append("Removed addition of zero")
                return node.right

        elif isinstance(node.op, ast.Mult):
            # x * 1 = x
            if isinstance(node.right, ast.Constant) and node.right.value == 1:
                self.transformations.append("Removed multiplication by one")
                return node.left
            # 1 * x = x
            elif isinstance(node.left, ast.Constant) and node.left.value == 1:
                self.transformations.append("Removed multiplication by one")
                return node.right
            # x * 0 = 0
            elif isinstance(node.right, ast.Constant) and node.right.value == 0:
                self.transformations.append("Optimized multiplication by zero")
                return ast.Constant(value=0)
            # 0 * x = 0
            elif isinstance(node.left, ast.Constant) and node.left.value == 0:
                self.transformations.append("Optimized multiplication by zero")  
                return ast.Constant(value=0)

        return self.generic_visit(node)

    def visit_If(self, node):
        """Optimize if statements."""
        # Remove if True: conditions
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.transformations.append("Removed always-true if condition")
            return node.body

        # Remove if False: conditions  
        elif isinstance(node.test, ast.Constant) and node.test.value is False:
            self.transformations.append("Removed always-false if condition")
            if node.orelse:
                return node.orelse
            else:
                return []  # Remove the entire if statement

        return self.generic_visit(node)


def transform_example():
    """Demonstrate AST transformations."""
    print("PyCompilerX AST Transformation Demo")
    print("=" * 40)

    # Example code to transform
    sample_code = """
def calculate(x, y):
    result = x + 0
    temp = y * 1  
    final = result + temp
    zero_mult = final * 0
    if True:
        return final + 5 * 3
    else:
        return 0

def math_operations():
    a = 10 + 5
    b = 20 - 8
    c = 6 * 7
    return a + b + c
"""

    print("Original code:")
    print(sample_code)

    print("\nOptimizing transformation:")
    print("-" * 50)

    try:
        # Apply optimizing transformation
        optimized_code, transformations = transform_code(sample_code, OptimizingTransformer)

        print("\nOptimized code:")
        print(optimized_code)

        if transformations:
            print("\nTransformations applied:")
            for i, transformation in enumerate(transformations, 1):
                print(f"{i}. {transformation}")
        else:
            print("\nNo optimizations were applied.")

    except Exception as e:
        print(f"Error in transformation: {e}")


def analyze_example():
    """Demonstrate code analysis capabilities."""
    print("\nCode Analysis Demo")
    print("=" * 30)

    sample_functions = [
        """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",

        """def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result""",

        """class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        return result""",

        """def complex_function(data):
    import math
    total = 0
    for i in range(len(data)):
        if data[i] > 0:
            total += math.sqrt(data[i])
    return total / len(data)"""
    ]

    for i, code in enumerate(sample_functions, 1):
        print(f"\nAnalyzing Code Sample {i}:")
        print("-" * 40)
        print(code)

        try:
            # Basic analysis
            analysis = analyze_code(code)
            print(f"\nCode Statistics:")
            print(f"  Functions: {analysis['functions']}")
            print(f"  Classes: {analysis['classes']}")
            print(f"  Variables: {len(analysis['variables'])} unique")
            print(f"  Loops: {analysis['loops']}")
            print(f"  Conditionals: {analysis['conditionals']}")
            print(f"  Function calls: {analysis['function_calls']}")
            print(f"  Imports: {len(analysis['imports'])}")

            # Show some variables
            if analysis['variables']:
                vars_to_show = list(analysis['variables'])[:5]
                print(f"  Sample variables: {vars_to_show}")

            # Type checking
            type_check = check_types(code)
            print(f"\nType Analysis:")
            print(f"  Success: {type_check['success']}")

            if type_check['errors']:
                print(f"  Errors ({len(type_check['errors'])}):")
                for error in type_check['errors'][:2]:  # Show first 2
                    print(f"    - {error}")

            if type_check['warnings']:
                print(f"  Warnings ({len(type_check['warnings'])}):")
                for warning in type_check['warnings'][:2]:  # Show first 2
                    print(f"    - {warning}")

            if type_check['symbol_table']:
                print(f"  Symbol table entries: {len(type_check['symbol_table'])}")

        except Exception as e:
            print(f"Error in analysis: {e}")


def ast_visualization_example():
    """Demonstrate AST visualization."""
    print("\nAST Visualization Demo")
    print("=" * 30)

    simple_expressions = [
        "x = 5",
        "y = x + 3",
        "result = (a + b) * 2"
    ]

    for expr in simple_expressions:
        print(f"\nExpression: {expr}")
        print("AST Structure:")
        try:
            tree = parse_code(expr)
            ast_repr = pretty_print_ast(tree)
            # Truncate long output
            lines = ast_repr.split('\n')
            if len(lines) > 15:
                truncated = lines[:15]
                truncated.append("... (truncated)")
                ast_repr = '\n'.join(truncated)
            print(ast_repr)
        except Exception as e:
            print(f"Error in AST visualization: {e}")


def optimization_showcase():
    """Show various optimization examples."""
    print("\nOptimization Showcase")
    print("=" * 30)

    test_codes = [
        "result = 5 + 3 * 2",
        "value = x + 0 + y * 1",
        "computation = 10 / 2 + 15 - 5",
        "final = (4 + 6) * (8 - 3)"
    ]

    for code in test_codes:
        print(f"\nOriginal: {code}")

        try:
            optimized, transformations = transform_code(code, OptimizingTransformer)
            print(f"Optimized: {optimized.strip()}")

            if transformations:
                print("Applied optimizations:")
                for opt in transformations:
                    print(f"  - {opt}")
            else:
                print("No optimizations applied")

        except Exception as e:
            print(f"Optimization failed: {e}")


if __name__ == "__main__":
    transform_example()
    analyze_example()
    ast_visualization_example()
    optimization_showcase()

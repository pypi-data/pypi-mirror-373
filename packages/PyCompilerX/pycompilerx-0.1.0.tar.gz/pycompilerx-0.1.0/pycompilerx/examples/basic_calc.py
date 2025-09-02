"""
Basic calculator example demonstrating parsing and evaluation
"""

import ast
from typing import Union, Dict, Any
from ..parsing.parser import parse_expression
from ..parsing.ast_tools import parse_code, analyze_code
from ..analysis.type_check import check_types


class BasicCalculator:
    """A basic calculator using PyCompilerX components."""

    def __init__(self):
        self.variables = {}
        self.history = []

    def evaluate_expression(self, expr: str) -> Union[int, float]:
        """
        Evaluate a mathematical expression.

        Args:
            expr: Mathematical expression string

        Returns:
            Numerical result
        """
        try:
            # Parse and evaluate using AST
            tree = parse_expression(expr)
            result = self._evaluate_ast(tree)

            # Store in history
            self.history.append(f"{expr} = {result}")

            return result

        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")

    def _evaluate_ast(self, node: ast.AST) -> Union[int, float]:
        """Evaluate an AST node recursively."""
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            # Variable lookup
            if node.id in self.variables:
                return self.variables[node.id]
            else:
                raise ValueError(f"Undefined variable: {node.id}")

        elif isinstance(node, ast.BinOp):
            left = self._evaluate_ast(node.left)
            right = self._evaluate_ast(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            elif isinstance(node.op, ast.Mod):
                return left % right
            elif isinstance(node.op, ast.FloorDiv):
                return left // right
            else:
                raise ValueError(f"Unsupported operation: {type(node.op)}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_ast(node.operand)

            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            else:
                raise ValueError(f"Unsupported unary operation: {type(node.op)}")

        else:
            raise ValueError(f"Unsupported AST node: {type(node)}")

    def set_variable(self, name: str, value: Union[int, float]):
        """Set a variable value."""
        self.variables[name] = value
        self.history.append(f"{name} = {value}")

    def get_variable(self, name: str) -> Union[int, float]:
        """Get a variable value."""
        if name not in self.variables:
            raise ValueError(f"Variable '{name}' is not defined")
        return self.variables[name]

    def list_variables(self) -> Dict[str, Union[int, float]]:
        """List all defined variables."""
        return self.variables.copy()

    def get_history(self) -> list:
        """Get calculation history."""
        return self.history.copy()

    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()

    def clear_variables(self):
        """Clear all variables."""
        self.variables.clear()

    def evaluate_script(self, script: str) -> Any:
        """
        Evaluate a multi-line script with assignments and expressions.

        Args:
            script: Multi-line Python script

        Returns:
            Result of the last expression
        """
        lines = [line.strip() for line in script.split('\n') if line.strip()]
        result = None

        for line in lines:
            if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
                # Variable assignment
                parts = line.split('=', 1)
                var_name = parts[0].strip()
                expr = parts[1].strip()
                value = self.evaluate_expression(expr)
                self.set_variable(var_name, value)
                result = value
            else:
                # Expression evaluation
                result = self.evaluate_expression(line)

        return result


def evaluate_expression(expr: str) -> Union[int, float]:
    """
    Quick function to evaluate a mathematical expression.

    Args:
        expr: Mathematical expression

    Returns:
        Numerical result
    """
    calc = BasicCalculator()
    return calc.evaluate_expression(expr)


def demo_calculator():
    """Demonstrate the basic calculator functionality."""
    print("PyCompilerX Basic Calculator Demo")
    print("=" * 40)

    calc = BasicCalculator()

    # Example calculations
    expressions = [
        "2 + 3",
        "10 * 5", 
        "15 / 3",
        "2 ** 3",
        "10 % 3",
        "17 // 5",
        "(2 + 3) * 4",
        "2 * (3 + 4) - 1"
    ]

    print("\nBasic arithmetic:")
    for expr in expressions:
        try:
            result = calc.evaluate_expression(expr)
            print(f"{expr:20} = {result}")
        except Exception as e:
            print(f"{expr:20} = Error: {e}")

    print("\nVariable usage:")
    calc.set_variable("x", 10)
    calc.set_variable("y", 5)

    variable_expressions = [
        "x + y",
        "x * y",
        "x ** 2",
        "x / y",
        "(x + y) * 2"
    ]

    for expr in variable_expressions:
        try:
            result = calc.evaluate_expression(expr)
            print(f"{expr:20} = {result}")
        except Exception as e:
            print(f"{expr:20} = Error: {e}")

    print("\nScript evaluation:")
    script = """
    a = 5
    b = 3
    c = a * b
    result = c + 10
    """

    try:
        final_result = calc.evaluate_script(script)
        print(f"Final result: {final_result}")
        print("Variables:", calc.list_variables())
    except Exception as e:
        print(f"Script error: {e}")


if __name__ == "__main__":
    demo_calculator()

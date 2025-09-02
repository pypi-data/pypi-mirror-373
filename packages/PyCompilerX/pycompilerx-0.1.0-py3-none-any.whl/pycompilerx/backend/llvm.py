"""
LLVM IR generation and compilation tools
"""

import ast
from typing import Dict, Any, Optional, List


class LLVMCodeGenerator(ast.NodeVisitor):
    """Generate LLVM IR from Python AST."""

    def __init__(self):
        self.ir_code = []
        self.variable_map = {}
        self.temp_counter = 0

    def generate_temp(self) -> str:
        """Generate a temporary variable name."""
        temp_name = f"%temp{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def emit(self, instruction: str):
        """Emit an LLVM instruction."""
        self.ir_code.append(instruction)

    def visit_Module(self, node):
        """Visit module node."""
        # LLVM IR header
        self.emit("; Generated LLVM IR from Python AST")
        self.emit('target triple = "x86_64-unknown-linux-gnu"')
        self.emit("")

        # Declare printf for output
        self.emit("declare i32 @printf(i8*, ...)")
        self.emit("")

        # Start main function
        self.emit("define i32 @main() {")
        self.emit("entry:")

        # Visit all statements
        self.generic_visit(node)

        # Return from main
        self.emit("  ret i32 0")
        self.emit("}")

    def visit_Assign(self, node):
        """Visit assignment statements."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

            if isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, int):
                    # Integer assignment
                    llvm_var = f"%{var_name}"
                    self.variable_map[var_name] = ('i32', llvm_var)
                    self.emit(f"  {llvm_var} = alloca i32")
                    self.emit(f"  store i32 {node.value.value}, i32* {llvm_var}")
                elif isinstance(node.value.value, float):
                    # Float assignment
                    llvm_var = f"%{var_name}"
                    self.variable_map[var_name] = ('double', llvm_var)
                    self.emit(f"  {llvm_var} = alloca double")
                    self.emit(f"  store double {node.value.value}, double* {llvm_var}")

        self.generic_visit(node)

    def visit_BinOp(self, node):
        """Visit binary operations."""
        # Generate LLVM IR for binary operations
        left_temp = self.generate_temp()
        right_temp = self.generate_temp()
        result_temp = self.generate_temp()

        # For demonstration, assume integer operations
        if isinstance(node.op, ast.Add):
            self.emit(f"  {result_temp} = add i32 {left_temp}, {right_temp}")
        elif isinstance(node.op, ast.Sub):
            self.emit(f"  {result_temp} = sub i32 {left_temp}, {right_temp}")
        elif isinstance(node.op, ast.Mult):
            self.emit(f"  {result_temp} = mul i32 {left_temp}, {right_temp}")
        elif isinstance(node.op, ast.Div):
            self.emit(f"  {result_temp} = sdiv i32 {left_temp}, {right_temp}")

        self.generic_visit(node)
        return result_temp

    def get_ir(self) -> str:
        """Get the generated LLVM IR code."""
        return "\n".join(self.ir_code)


def generate_llvm_ir(code: str) -> str:
    """
    Generate LLVM IR from Python code.

    Args:
        code: Python source code

    Returns:
        LLVM IR as string
    """
    try:
        tree = ast.parse(code)
        generator = LLVMCodeGenerator()
        generator.visit(tree)
        return generator.get_ir()
    except Exception as e:
        return f"; Error generating LLVM IR: {e}"


class SimpleLLVMIR:
    """Simple LLVM IR generator for basic operations."""

    def __init__(self):
        self.instructions = []
        self.variables = {}

    def declare_variable(self, name: str, var_type: str = "i32"):
        """Declare a variable."""
        var_ref = f"%{name}"
        self.variables[name] = (var_type, var_ref)
        self.instructions.append(f"  {var_ref} = alloca {var_type}")

    def store_value(self, var_name: str, value: Any):
        """Store a value in a variable."""
        if var_name not in self.variables:
            if isinstance(value, float):
                self.declare_variable(var_name, "double")
            else:
                self.declare_variable(var_name, "i32")

        var_type, var_ref = self.variables[var_name]
        if var_type == "i32" and isinstance(value, int):
            self.instructions.append(f"  store i32 {value}, i32* {var_ref}")
        elif var_type == "double" and isinstance(value, (int, float)):
            self.instructions.append(f"  store double {float(value)}, double* {var_ref}")

    def generate_function(self, function_name: str = "main") -> str:
        """Generate complete LLVM IR function."""
        ir_lines = [
            "; Generated LLVM IR",
            'target triple = "x86_64-unknown-linux-gnu"',
            "",
            f"define i32 @{function_name}() {{",
            "entry:"
        ]

        ir_lines.extend(self.instructions)

        ir_lines.extend([
            "  ret i32 0",
            "}"
        ])

        return "\n".join(ir_lines)


def compile_to_llvm(python_expr: str) -> str:
    """
    Compile a simple Python expression to LLVM IR.

    Args:
        python_expr: Simple Python expression (e.g., "x = 5 + 3")

    Returns:
        LLVM IR code
    """
    try:
        # Parse the expression
        tree = ast.parse(python_expr)

        # Create LLVM IR generator
        llvm_gen = SimpleLLVMIR()

        # Simple compilation for assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                    var_name = target.id
                    value = node.value.value
                    llvm_gen.store_value(var_name, value)

        return llvm_gen.generate_function()

    except Exception as e:
        return f"; Error: {e}"


def optimize_llvm_ir(ir_code: str) -> Dict[str, Any]:
    """
    Mock LLVM optimization function.

    Args:
        ir_code: LLVM IR code

    Returns:
        Dictionary with optimization results
    """
    # Count instructions for mock optimization metrics
    lines = ir_code.strip().split('\n')
    instructions = [line for line in lines if line.strip() and not line.strip().startswith(';')]

    return {
        'original_instructions': len(instructions),
        'optimized_instructions': max(1, len(instructions) - 2),  # Mock optimization
        'optimizations_applied': [
            'dead_code_elimination',
            'constant_propagation',
            'instruction_combining'
        ],
        'size_reduction': '15%',
        'estimated_speedup': '1.2x'
    }

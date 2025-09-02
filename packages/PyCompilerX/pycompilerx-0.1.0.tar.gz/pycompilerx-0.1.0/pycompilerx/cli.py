"""
Command-line interface for PyCompilerX
"""

import argparse
import sys
from typing import Optional

from . import __version__
from .parsing.ast_tools import parse_code, analyze_code, validate_syntax
from .analysis.type_check import check_types, analyze_types
from .backend.llvm import generate_llvm_ir, optimize_llvm_ir
from .backend.cython import compile_cython, analyze_cython_potential
from .backend.numba import analyze_numba_compatibility
from .examples.basic_calc import BasicCalculator


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pycompilerx",
        description="PyCompilerX - A Comprehensive Python Compiler Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pycompilerx analyze script.py --types     # Analyze with type checking
  pycompilerx parse -e "x = 5 + 3"        # Parse expression
  pycompilerx compile --llvm script.py     # Generate LLVM IR
  pycompilerx calc "2 + 3 * 4"            # Calculator
        """
    )

    parser.add_argument(
        "--version", action="version", version=f"PyCompilerX {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse Python code")
    parse_parser.add_argument("file", nargs="?", help="Python file to parse")
    parse_parser.add_argument("-e", "--expression", help="Python expression to parse")
    parse_parser.add_argument("--validate", action="store_true", help="Validate syntax only")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze Python code")
    analyze_parser.add_argument("file", help="Python file to analyze")
    analyze_parser.add_argument("--types", action="store_true", help="Include type checking")
    analyze_parser.add_argument("--stats", action="store_true", help="Show detailed statistics")
    analyze_parser.add_argument("--cython", action="store_true", help="Analyze Cython potential")
    analyze_parser.add_argument("--numba", action="store_true", help="Analyze Numba potential")

    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile Python code")
    compile_parser.add_argument("file", help="Python file to compile")
    compile_parser.add_argument("--llvm", action="store_true", help="Generate LLVM IR")
    compile_parser.add_argument("--cython", action="store_true", help="Compile with Cython")
    compile_parser.add_argument("-o", "--output", help="Output file")
    compile_parser.add_argument("--optimize", action="store_true", help="Apply optimizations")

    # Calculator command
    calc_parser = subparsers.add_parser("calc", help="Calculator mode")
    calc_parser.add_argument("expression", nargs="?", help="Expression to evaluate")
    calc_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    calc_parser.add_argument("-s", "--script", help="Evaluate script file")

    return parser


def handle_parse_command(args) -> int:
    """Handle parse command."""
    try:
        if args.expression:
            code = args.expression
            source = "expression"
        elif args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()
            source = args.file
        else:
            print("Error: Provide either --expression or a file")
            return 1

        if args.validate:
            # Just validate syntax
            validation = validate_syntax(code)
            if validation['valid']:
                print(f"✓ Syntax is valid for {source}")
            else:
                print(f"✗ {validation['message']}")
                return 1
        else:
            # Parse and show info
            tree = parse_code(code)
            print(f"✓ Parsing successful for {source}")
            print(f"Code length: {len(code)} characters")
            print(f"AST node type: {type(tree).__name__}")

        return 0

    except FileNotFoundError:
        print(f"Error: File {args.file} not found")
        return 1
    except Exception as e:
        print(f"Parse error: {e}")
        return 1


def handle_analyze_command(args) -> int:
    """Handle analyze command."""
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()

        print(f"Analyzing: {args.file}")
        print("=" * 60)

        # Basic syntax validation
        validation = validate_syntax(code)
        if not validation['valid']:
            print(f"✗ Syntax Error: {validation['message']}")
            return 1

        print("✓ Syntax is valid")

        # Code analysis
        if args.stats or not any([args.types, args.cython, args.numba]):
            analysis = analyze_code(code)
            print("\nCode Statistics:")
            print(f"  Functions: {analysis['functions']}")
            print(f"  Classes: {analysis['classes']}")
            print(f"  Variables: {len(analysis['variables'])}")
            print(f"  Loops: {analysis['loops']}")
            print(f"  Conditionals: {analysis['conditionals']}")
            print(f"  Function calls: {analysis['function_calls']}")
            print(f"  Imports: {len(analysis['imports'])}")

            if analysis['variables']:
                sample_vars = list(analysis['variables'])[:10]
                print(f"  Sample variables: {sample_vars}")

        # Type checking
        if args.types:
            print("\nType Analysis:")
            type_result = check_types(code)
            if type_result['success']:
                print("  ✓ Type checking passed")
            else:
                print("  ⚠ Type checking found issues")

            if type_result['errors']:
                print(f"  Errors ({len(type_result['errors'])}):")
                for error in type_result['errors'][:5]:
                    print(f"    - {error}")

            if type_result['warnings']:
                print(f"  Warnings ({len(type_result['warnings'])}):")
                for warning in type_result['warnings'][:5]:
                    print(f"    - {warning}")

            if type_result['symbol_table']:
                print(f"  Symbol table: {len(type_result['symbol_table'])} entries")

        # Cython analysis
        if args.cython:
            print("\nCython Optimization Analysis:")
            cython_analysis = analyze_cython_potential(code)
            if 'error' in cython_analysis:
                print(f"  Error: {cython_analysis['error']}")
            else:
                print(f"  Optimization potential: {cython_analysis['optimization_potential']}")
                print(f"  Has loops: {cython_analysis['has_loops']}")
                print(f"  Has numeric operations: {cython_analysis['has_numeric_ops']}")
                if cython_analysis['suggestions']:
                    print("  Suggestions:")
                    for suggestion in cython_analysis['suggestions']:
                        print(f"    - {suggestion}")

        # Numba analysis
        if args.numba:
            print("\nNumba JIT Analysis:")
            # For file analysis, we'll analyze the first function we find
            try:
                tree = parse_code(code)
                func_found = False
                for node in tree.body:
                    if hasattr(node, 'name') and callable(getattr(node, 'name', None)):
                        # Create a mock function for analysis
                        def mock_func():
                            pass
                        mock_func.__name__ = getattr(node, 'name', 'unknown')

                        numba_analysis = analyze_numba_compatibility(mock_func)
                        print(f"  Function: {numba_analysis['function_name']}")
                        print(f"  Compatible: {numba_analysis['is_compatible']}")
                        print(f"  Estimated speedup: {numba_analysis['estimated_speedup']}")

                        if numba_analysis['issues']:
                            print("  Issues:")
                            for issue in numba_analysis['issues']:
                                print(f"    - {issue}")

                        if numba_analysis['recommendations']:
                            print("  Recommendations:")
                            for rec in numba_analysis['recommendations']:
                                print(f"    - {rec}")

                        func_found = True
                        break

                if not func_found:
                    print("  No functions found for Numba analysis")
            except Exception as e:
                print(f"  Analysis error: {e}")

        return 0

    except FileNotFoundError:
        print(f"Error: File {args.file} not found")
        return 1
    except Exception as e:
        print(f"Analysis error: {e}")
        return 1


def handle_compile_command(args) -> int:
    """Handle compile command."""
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()

        print(f"Compiling: {args.file}")
        print("=" * 50)

        if args.llvm:
            print("Generating LLVM IR...")
            llvm_ir = generate_llvm_ir(code)

            if args.optimize:
                print("Applying LLVM optimizations...")
                opt_result = optimize_llvm_ir(llvm_ir)
                print(f"Optimization results:")
                print(f"  Instructions reduced: {opt_result['original_instructions']} -> {opt_result['optimized_instructions']}")
                print(f"  Size reduction: {opt_result['size_reduction']}")
                print(f"  Estimated speedup: {opt_result['estimated_speedup']}")

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(llvm_ir)
                print(f"✓ LLVM IR written to: {args.output}")
            else:
                print("\nGenerated LLVM IR:")
                print("-" * 40)
                print(llvm_ir)

        elif args.cython:
            print("Compiling with Cython...")
            result = compile_cython(code, args.optimize)

            if result['success']:
                print("✓ Cython compilation successful!")
                print(f"Performance gain: {result['performance_gain']}")
                print(f"Code size: {result['size_kb']:.2f} KB")

                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(result['cython_code'])
                    print(f"✓ Cython code written to: {args.output}")
                else:
                    print("\nGenerated Cython code:")
                    print("-" * 40)
                    print(result['cython_code'])
            else:
                print(f"✗ Cython compilation failed: {result['error']}")
                return 1

        else:
            print("Error: Specify compilation target (--llvm or --cython)")
            return 1

        return 0

    except FileNotFoundError:
        print(f"Error: File {args.file} not found")
        return 1
    except Exception as e:
        print(f"Compilation error: {e}")
        return 1


def handle_calc_command(args) -> int:
    """Handle calculator command."""
    calc = BasicCalculator()

    if args.script:
        # Evaluate script file
        try:
            with open(args.script, 'r') as f:
                script_content = f.read()
            result = calc.evaluate_script(script_content)
            print(f"Script result: {result}")
            print("Final variables:", calc.list_variables())
            return 0
        except FileNotFoundError:
            print(f"Error: Script file {args.script} not found")
            return 1
        except Exception as e:
            print(f"Script error: {e}")
            return 1

    elif args.interactive:
        print("PyCompilerX Interactive Calculator")
        print("Type expressions or 'var = expr' for assignments")
        print("Type 'exit', 'quit', or Ctrl+C to exit")
        print("=" * 50)

        while True:
            try:
                expr = input(">>> ").strip()
                if expr.lower() in ['exit', 'quit']:
                    break

                if not expr:
                    continue

                if '=' in expr and not any(op in expr for op in ['==', '!=', '<=', '>=']):
                    # Variable assignment
                    parts = expr.split('=', 1)
                    var_name = parts[0].strip()
                    var_expr = parts[1].strip()
                    value = calc.evaluate_expression(var_expr)
                    calc.set_variable(var_name, value)
                    print(f"{var_name} = {value}")
                else:
                    # Expression evaluation
                    result = calc.evaluate_expression(expr)
                    print(f"= {result}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nGoodbye!")
        return 0

    elif args.expression:
        try:
            result = calc.evaluate_expression(args.expression)
            print(f"{args.expression} = {result}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    else:
        print("Error: Provide an expression, use --interactive mode, or specify --script")
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    try:
        parser = create_parser()
        args = parser.parse_args(argv)

        if not args.command:
            parser.print_help()
            return 1

        if args.command == "parse":
            return handle_parse_command(args)
        elif args.command == "analyze":
            return handle_analyze_command(args)
        elif args.command == "compile":
            return handle_compile_command(args)
        elif args.command == "calc":
            return handle_calc_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

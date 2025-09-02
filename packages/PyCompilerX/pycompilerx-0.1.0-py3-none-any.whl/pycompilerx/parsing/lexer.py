"""
Lexical analyzer for Python code using tokenize module
"""

import tokenize
import io
from typing import List, Tuple


class PythonLexer:
    """A lexical analyzer for Python source code."""

    def __init__(self):
        self.tokens = []

    def tokenize_string(self, code: str) -> List[Tuple[str, str, Tuple[int, int]]]:
        """
        Tokenize a Python code string.

        Args:
            code: Python source code as string

        Returns:
            List of tuples containing (token_type, token_string, position)
        """
        tokens = []
        code_bytes = code.encode('utf-8')

        try:
            from token import tok_name
            tokens_iter = tokenize.tokenize(io.BytesIO(code_bytes).readline)
            for token in tokens_iter:
                token_type = tok_name.get(token.type, 'UNKNOWN')
                token_string = token.string
                position = (token.start[0], token.start[1])
                tokens.append((token_type, token_string, position))
        except tokenize.TokenError as e:
            raise ValueError(f"Tokenization error: {e}")

        return tokens

    def tokenize_file(self, filepath: str) -> List[Tuple[str, str, Tuple[int, int]]]:
        """
        Tokenize a Python file.

        Args:
            filepath: Path to Python file

        Returns:
            List of tuples containing (token_type, token_string, position)
        """
        try:
            with open(filepath, 'rb') as f:
                from token import tok_name
                tokens = []
                tokens_iter = tokenize.tokenize(f.readline)
                for token in tokens_iter:
                    token_type = tok_name.get(token.type, 'UNKNOWN')
                    token_string = token.string
                    position = (token.start[0], token.start[1])
                    tokens.append((token_type, token_string, position))
            return tokens
        except (IOError, tokenize.TokenError) as e:
            raise ValueError(f"Error tokenizing file {filepath}: {e}")

    def get_keywords(self, tokens: List[Tuple[str, str, Tuple[int, int]]]) -> List[str]:
        """Extract Python keywords from tokenized code."""
        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'True', 'False', 'None'
        ]

        keywords = []
        for token_type, token_string, _ in tokens:
            if token_type == 'NAME' and token_string in python_keywords:
                keywords.append(token_string)
        return keywords


def quick_tokenize(code: str) -> List[Tuple[str, str]]:
    """
    Quick tokenization function for simple use cases.

    Args:
        code: Python source code

    Returns:
        List of (token_type, token_value) tuples
    """
    lexer = PythonLexer()
    tokens = lexer.tokenize_string(code)
    return [(token_type, token_string) for token_type, token_string, _ in tokens]

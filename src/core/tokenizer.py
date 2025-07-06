import re
from enum import Enum, auto
from typing import Generator, NamedTuple
from core.core_types.tokens import TokType, Token


class Tokenizer:
    """
    Tokenizer class for lexical analysis of command-line input.
    This class uses regular expressions to tokenize input strings into a sequence of tokens,
    such as commands, flags, logical operators, strings, and other syntactic elements.
    It supports skipping whitespace, handling both single and double-quoted strings,
    and raises syntax errors for unexpected characters.
    Attributes:
        patterns (list): A list of tuples mapping token types to their regex patterns.
        master_pattern (re.Pattern): The compiled master regex pattern for tokenization.
    Methods:
        __init__():
            Initializes the tokenizer with regex patterns for different token types.
        tokenize(text: str) -> Generator[Token, None, None]:
            Skips whitespace tokens, removes quotes from string tokens, and yields an EOF token at the end.
            Raises SyntaxError for unexpected characters.
    """

    def __init__(self):
        self.patterns = [
            (TokType.WHITESPACE, r"\s+"),
            (TokType.AND, r"&&"),
            (TokType.OR, r"\|\|"),
            (TokType.SEMI, r";"),
            (TokType.FLAG, r"--?\w+"),
            (TokType.STRING, r'"([^"\\]*(\\.[^"\\]*)*)"'),  # Double quotes
            (TokType.STRING, r"'([^'\\]*(\\.[^'\\]*)*)'"),  # Single quotes
            (TokType.COMMAND, r"[a-zA-Z0-9_-]+"),
            (TokType.MISMATCH, r"."),  # Catch any other character
        ]
        parts = []
        for idx, (tok_type, pattern) in enumerate(self.patterns):
            parts.append(f"(?P<T{idx}>{pattern})")
        self.master_pattern = re.compile("|".join(parts))

    def tokenize(self, text: str) -> Generator[Token, None, None]:
        """
        Tokenizes the input text and yields Token objects for each recognized token.

        Args:
            text (str): The input string to tokenize.

        Yields:
            Token: A token object representing the next token in the input text.

        Raises:
            SyntaxError: If an unexpected character is encountered in the input text.

        Notes:
            - Whitespace tokens are skipped and not yielded.
            - If a string token is matched, its surrounding quotes are removed before yielding.
            - At the end of the input, an EOF (end-of-file) token is yielded.
        """
        pos = 0
        while pos < len(text):
            match = self.master_pattern.match(text, pos)
            if not match:
                raise SyntaxError(
                    f"Unexpected character: {text[pos]!r} at position {pos}"
                )
            for idx, (tok_type, _) in enumerate(self.patterns):
                group = match.group(f"T{idx}")
                if group is not None:
                    if tok_type == TokType.WHITESPACE:
                        pos = match.end()
                        break
                    if tok_type == TokType.MISMATCH:
                        raise SyntaxError(
                            f"Unexpected character: {group!r} at position {pos}"
                        )
                    if tok_type == TokType.STRING:
                        group = group[1:-1]
                    yield Token(tok_type, group)
                    pos = match.end()
                    break
        yield Token(TokType.EOF, "")


if __name__ == "__main__":
    test_input = r"echo 'Hello, World!' && ls -l | grep 'txt' ; echo $HOME/bin/script.sh --verbose"
    tokenizer = Tokenizer()
    try:
        for token in tokenizer.tokenize(test_input):
            print(f"Type: {token.type}, Value: {token.value}")
    except SyntaxError as e:
        print("Syntax error:", e)

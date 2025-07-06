from enum import Enum, auto
from typing import NamedTuple

class TokType(Enum):
    """
    Enumeration of token types used for parsing command-line input.

    Attributes:
        COMMAND: Represents a command token.
        STRING: Represents a string or argument token.
        FLAG: Represents a flag or option token (e.g., -h, --help).
        AND: Represents a logical AND operator (e.g., &&).
        OR: Represents a logical OR operator (e.g., ||).
        SEMI: Represents a semicolon (;) used to separate commands.
        EOF: Represents the end-of-file/input token.
        WHITESPACE: Represents whitespace characters (e.g., spaces, tabs).
        MISMATCH: Represents an unrecognized or invalid token.
    """
    COMMAND = auto()
    STRING = auto()
    FLAG = auto()
    AND = auto()
    OR = auto()
    SEMI = auto()
    EOF = auto()
    WHITESPACE = auto()
    MISMATCH = auto()

class Token(NamedTuple):
    type: TokType
    value: str

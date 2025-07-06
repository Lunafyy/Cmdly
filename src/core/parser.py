from typing import List
from collections import deque
from core.core_types.tokens import Token, TokType


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = deque(tokens)
        self.current = None
        self.next_token()

    def next_token(self):
        """
        Advances to the next token in the token stream.

        If there are remaining tokens, sets `self.current` to the next token by removing it from the left of the deque.
        If no tokens remain, sets `self.current` to an EOF (end-of-file) token.
        """
        self.current = self.tokens.popleft() if self.tokens else Token(TokType.EOF, "")

    def parse(self):
        """
        Parses a sequence of tokens into chains until the end of file (EOF) token is reached.

        Returns:
            list: A list of parsed chains, where each chain is produced by the `parse_chain` method.
        """
        chains = []
        while self.current.type != TokType.EOF:
            chain = self.parse_chain()
            chains.append(chain)
            if self.current.type in {TokType.SEMI, TokType.AND, TokType.OR}:
                separator = self.current.type.name
                self.next_token()
            else:
                separator = None
            if separator:
                pass
        return chains

    def parse_chain(self):
        """
        Parses a command chain and returns a dictionary representing the command.

        Returns:
            dict: A dictionary with a "type" key set to "COMMAND" and additional keys/values
                  from the parsed command.
        """
        return {"type": "COMMAND", **self.parse_command()}

    def parse_command(self):
        """
        Parses a command and its arguments from the current token stream.
        Returns:
            dict: A dictionary with the following structure:
                {
                    "cmd": str,
                    "args": list,
                    "kwargs": dict
                }
        Raises:
            SyntaxError: If the current token is not a command.
        Parsing rules:
            - The first token must be of type COMMAND.
            - Flags (tokens of type FLAG) are parsed as keyword arguments. If a flag contains '=', it is split into key-value.
              Otherwise, if followed by a COMMAND or STRING token, its value is set to that token's value; else, it is set to True.
            - Tokens of type COMMAND or STRING are parsed as positional arguments unless they contain '=', in which case they are
              treated as keyword arguments.
            - Parsing stops at tokens of type AND, OR, SEMI, or EOF.
        """
        if self.current.type != TokType.COMMAND:
            raise SyntaxError(f"Expected command, got {self.current.type}")
        cmd = self.current.value
        self.next_token()

        args = []
        kwargs = {}

        while self.current.type not in {
            TokType.AND,
            TokType.OR,
            TokType.SEMI,
            TokType.EOF,
        }:
            if self.current.type == TokType.FLAG:
                flag = self.current.value.lstrip("-")
                if "=" in flag:
                    k, v = flag.split("=", 1)
                    kwargs[k] = v
                    self.next_token()
                else:
                    self.next_token()
                    if self.current.type in {TokType.COMMAND, TokType.STRING}:
                        kwargs[flag] = self.current.value
                        self.next_token()
                    else:
                        kwargs[flag] = True
            elif self.current.type in {TokType.COMMAND, TokType.STRING}:
                val = self.current.value
                if "=" in val:
                    k, v = val.split("=", 1)
                    kwargs[k] = v
                else:
                    args.append(val)
                self.next_token()
            else:
                break
        return {"cmd": cmd, "args": args, "kwargs": kwargs}


if __name__ == "__main__":
    tokens = [
        Token(TokType.COMMAND, "echo"),
        Token(TokType.STRING, "Hello, World!"),
        Token(TokType.FLAG, "--verbose"),
        Token(TokType.EOF, ""),
        Token(TokType.AND, "&&"),
        Token(TokType.COMMAND, "ls"),
        Token(TokType.FLAG, "-l"),
        Token(TokType.AND, "CJ"),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    import pprint

    pprint.pprint(ast)

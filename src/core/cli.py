import colorama
import os
from art import tprint
from core.utils import Utils
from core.tokenizer import Tokenizer
from core.parser import Parser
from core.executor import Executor
from core.config_loader import Config
from core.logger import get_logger

colorama.init(autoreset=True)


class CLI:
    """
    CLI class provides a command-line interface loop for processing user commands.
    Attributes:
        tokenizer: An object responsible for tokenizing user input.
        parser_cls: The parser class used to parse tokenized input.
        executor: An object responsible for executing parsed commands.
        running (bool): Indicates whether the CLI loop is active.
        config (dict): Configuration settings for the CLI, loaded from Config.
    Methods:
        __init__(tokenizer, parser_cls, executor):
            Initializes the CLI with the given tokenizer, parser class, and executor.
            Loads configuration settings.
        run():
            Starts the main CLI loop, displaying a welcome message, logging startup information,
            and repeatedly prompting the user for input. Handles special commands, tokenizes and parses
            input, executes commands, and manages errors and keyboard interrupts gracefully.
        _handle_special_commands(raw_input):
            Handles special commands such as 'exit' and 'quit'. Prints a goodbye message,
            logs the exit event, and stops the CLI loop if a special command is detected.
        _print_output(output):
        _print_error(error_msg):
    """

    def __init__(self, tokenizer, parser_cls, executor):
        self.tokenizer = tokenizer
        self.parser_cls = parser_cls
        self.executor = executor
        self.running = True
        self.config = Config.get_config()

    def run(self):
        """
        Runs the main CLI loop, displaying a welcome message, logging startup information, and repeatedly prompting the user for input.
        Processes user commands, handles special commands, tokenizes and parses input, and executes commands.
        Catches and displays errors, and handles keyboard interrupts gracefully by triggering the exit command.
        Raises:
            Exception: If an error occurs during command processing.
            KeyboardInterrupt: If the user interrupts the CLI with Ctrl+C.
        """
        Utils.welcome_message()
        get_logger("cli").info("Starting Cmdly CLI")
        get_logger("cli").info("Current configuration: %s", self.config)

        while self.running:
            try:
                prompt = self.config.get("prompt").get("format")
                prompt = prompt.replace(
                    "{emoji}", self.config.get("prompt").get("emoji", "")
                )
                prompt = prompt.replace("{username}", os.getlogin())

                raw_input = input(prompt).strip()

                get_logger("cli").info(f"User input: {raw_input}")

                if self._handle_special_commands(raw_input):
                    continue

                tokens = self.tokenizer.tokenize(raw_input)
                parser = self.parser_cls(tokens)
                command_structs = parser.parse()

                for cmd_struct in command_structs:
                    success = self.executor.execute_command(cmd_struct)

            except Exception as e:
                self._print_error(f"Error: {e}")
            except KeyboardInterrupt:
                self._handle_special_commands("exit")

    def _handle_special_commands(self, raw_input):
        """
        Handles special CLI commands such as 'exit' and 'quit'.
        Parameters:
            raw_input (str): The raw input string entered by the user.
        Returns:
            bool: True if a special command was handled (e.g., exit or quit), False otherwise.
        Side Effects:
            - Prints a goodbye message and logs the exit event if a special command is detected.
            - Sets self.running to False to terminate the CLI loop.
        """
        if raw_input.lower() in ("exit", "quit"):
            print("Goodbye! 👋")
            get_logger("cli").info("Exiting Cmdly CLI")
            self.running = False
            return True

        return False

    def _print_output(self, output):
        """
        Prints the provided output to the standard output.

        Args:
            output (Any): The data to be printed to the console.
        """
        print(output)

    def _print_error(self, error_msg):
        """
        Prints the given error message to the console in red color.

        Args:
            error_msg (str): The error message to display.
        """
        print(f"\033[91m{error_msg}\033[0m")


def main():
    """
    Initializes the core components of the CLI application and starts the command-line interface loop.

    This function creates instances of the Tokenizer, Executor, and CLI classes,
    then invokes the CLI's run method to begin processing user input.
    """
    tokenizer = Tokenizer()
    executor = Executor()
    cli = CLI(tokenizer, Parser, executor)
    cli.run()

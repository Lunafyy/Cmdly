import os
import importlib
import colorama
from core.core_types.command import BaseCommand
from core.logger import get_logger

colorama.init(autoreset=True)


class Help(BaseCommand):
    """
    Dynamically loads command modules and displays help.
    """

    author = "CJ"
    date_created = "2025-06-17"
    description = "Displays help information for available commands."
    help = "Usage: help [command]"
    fun = False

    def execute(self, *args, **kwargs):
        """
        Executes the help command, displaying information about available commands or detailed help for a specific command.
        Args:
            *args: Optional positional arguments. If provided, the first argument is treated as the command name to display detailed help for.
            **kwargs: Optional keyword arguments (not used).
        Behavior:
            - If a command name is provided in args, attempts to load and display its description and help text.
            - If no command name is provided, lists all available commands in the commands directory, showing their descriptions.
            - Marks commands with a 'fun' attribute as [FUN COMMAND].
            - Logs errors and missing commands using the application's logger.
            - Returns 0 upon completion.
        """
        commands_path = os.path.join(os.path.dirname(__file__), "..", "commands")
        commands_path = os.path.abspath(commands_path)

        if args:
            command_name = args[0].lower()
            try:
                module = importlib.import_module(f"commands.{command_name}")
                get_logger("help").info(f"Loading command: {command_name}")
                command_class = self._get_command_class(module)
                if command_class:
                    print(f"{command_name} - {command_class.description}")
                    print(command_class.help)
                else:
                    print(f"No valid command class found in {command_name}")
                    get_logger("help").error(
                        f"No valid command class found in {command_name}"
                    )
            except ModuleNotFoundError:
                print(f"Command not found: {command_name}")
                get_logger("help").error(f"Command not found: {command_name}")
        else:
            print("Available commands:\n")
            for file in os.listdir(commands_path):
                if file.endswith(".py") and not file.startswith("__"):
                    name = file[:-3]
                    try:
                        module = importlib.import_module(f"commands.{name}")
                        command_class = self._get_command_class(module)

                        if command_class and getattr(command_class, "fun", False):
                            print(
                                f"  {name:<10} - {command_class.description} - {colorama.Fore.MAGENTA}[FUN COMMAND]{colorama.Style.RESET_ALL}"
                            )
                        elif command_class:
                            print(f"  {name:<10} - {command_class.description}")
                    except Exception as e:
                        print(f"  {name:<10} - [Error loading: {e}]")
                        get_logger("help").error(f"Error loading command '{name}': {e}")

            print("\nUse 'help [command]' for more info.")
        return 0

    def _get_command_class(self, module):
        """
        Extracts and returns the first class in the given module that is a subclass of BaseCommand (excluding BaseCommand itself).

        Args:
            module (module): The module to search for a command class.

        Returns:
            type or None: The first found subclass of BaseCommand, or None if no such class exists.
        """
        for attr in dir(module):
            obj = getattr(module, attr)
            if (
                isinstance(obj, type)
                and issubclass(obj, BaseCommand)
                and obj != BaseCommand
            ):
                return obj
        return None

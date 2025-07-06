import importlib
import inspect
from typing import List, Dict, Any
from core.config_loader import Config
from core.core_types.command import BaseCommand
from core.logger import get_logger


class Executor:
    """
    Executor is responsible for running command chains, resolving command aliases, and executing individual commands.
    Attributes:
        commands_module (str): The base module path where command modules are located.
        aliases (dict): A mapping of command aliases to their actual command names, loaded from configuration.
    Methods:
        __init__(commands_module: str = "commands"):
            Initializes the Executor with the specified commands module and loads command aliases from configuration.
        run(chains: List[Dict[str, Any]]) -> bool:
            Executes a sequence of command chains. Each chain should specify a "type" (default "COMMAND").
            Only chains of type "COMMAND" are executed; others are skipped with a message.
            Returns True if the last command succeeded, otherwise False.
        resolve_alias(command: str) -> str:
            Resolves a command alias to its actual command name using the loaded aliases.
            Returns the original command if no alias is found.
        execute_command(cmd_dict: Dict[str, Any]) -> bool:
            Executes a command specified by a dictionary containing the command name or alias, arguments, and keyword arguments.
            Dynamically imports the command module, resolves the command class, checks feature flags, and executes the command.
            Returns True if the command executed successfully, False otherwise.
            Raises ModuleNotFoundError if the command module or class cannot be found.
    """

    def __init__(self, commands_module: str = "commands"):
        self.commands_module = commands_module
        self.aliases = Config.get_config().get("aliases", {})

    def run(self, chains: List[Dict[str, Any]]):
        """
        Executes a sequence of command chains.

        Args:
            chains (List[Dict[str, Any]]): A list of dictionaries, each representing a command chain.
                Each dictionary should contain at least a "type" key, which specifies the type of the chain.
                If "type" is "COMMAND", the command is executed using `self.execute_command`.

        Returns:
            bool: The status of the last executed command chain. Returns True if the last command succeeded, otherwise False.

        Notes:
            - If a chain type other than "COMMAND" is encountered, a message is printed and the chain is skipped.
        """
        last_status = True
        for chain in chains:
            cmd_type = chain.get("type", "COMMAND")
            if cmd_type == "COMMAND":
                last_status = self.execute_command(chain)
            else:
                print(f"Unsupported chain type: {cmd_type}")
        return last_status

    def resolve_alias(self, command: str) -> str:
        """
        Resolves a command alias to its actual command name.

        If the provided command matches a known alias, returns the corresponding actual command name.
        Otherwise, returns the command unchanged.

        Args:
            command (str): The command or alias to resolve.

        Returns:
            str: The resolved actual command name, or the original command if no alias is found.
        """
        return self.aliases.get(command, command)

    def execute_command(self, cmd_dict: Dict[str, Any]) -> bool:
        """
        Executes a command specified by the given command dictionary.
        This method dynamically imports the command module, resolves the command class,
        checks for feature flags, and executes the command
        with the provided arguments and keyword arguments.
        Args:
            cmd_dict (Dict[str, Any]): A dictionary containing the command information.
                Expected keys:
                    - "cmd": The name or alias of the command to execute.
                    - "args": (Optional) List of positional arguments for the command.
                    - "kwargs": (Optional) Dictionary of keyword arguments for the command.
        Returns:
            bool: True if the command executed successfully, False otherwise.
        Raises:
            ModuleNotFoundError: If the command module or class cannot be found.
        """
        cmd_name = cmd_dict.get("cmd")
        cmd_name = self.resolve_alias(cmd_name)
        args = cmd_dict.get("args", [])
        kwargs = cmd_dict.get("kwargs", {})

        try:
            module = importlib.import_module(
                f"{self.commands_module}.{cmd_name.lower()}"
            )
            CommandClass = None
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseCommand) and obj is not BaseCommand:
                    CommandClass = obj
                    break

            if getattr(CommandClass, "fun", False) and not Config.get_config().get(
                "features", {}
            ).get("fun_commands", True):
                print(
                    "⚠️  Fun commands are currently disabled. Please enable them in the configuration. (config/default_settings.json)"
                )
                get_logger("executor").warning(
                    "User attempted to run a fun command while fun commands are disabled."
                )
                return True
        except (ModuleNotFoundError, AttributeError) as e:
            print(e)
            get_logger("executor").error(f"Error loading command '{cmd_name}': {e}")
            raise ModuleNotFoundError(f"Command not found: {cmd_name}")
            return False

        try:
            cmd_instance = CommandClass()
            result = cmd_instance.execute(*args, **kwargs)
            if result != 0:
                get_logger("executor").error(
                    f"Command '{cmd_name}' failed with exit code {result}"
                )
                print(f"Command '{cmd_name}' failed with exit code {result}")
                return False
            return True
        except Exception as e:
            get_logger("executor").error(f"Error executing command '{cmd_name}': {e}")
            print(f"Error running command '{cmd_name}': {e}")
            return False


if __name__ == "__main__":
    executor = Executor()
    chains = [
        {"args": ["Hello, World!"], "cmd": "echo", "kwargs": {}, "type": "COMMAND"}
    ]
    success = executor.run(chains)
    print(f"Execution finished with status: {success}")

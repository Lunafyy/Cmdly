from core.core_types.command import BaseCommand
from core.logger import get_logger


class Echo(BaseCommand):
    """
    Echo command that prints its arguments to the console.
    """

    author = "Lunafy"
    date_created = "2025-06-17"
    description = "Echoes the provided arguments."
    help = "Usage: echo <message> [options]"
    fun = False

    def execute(self, *args, **kwargs):
        """
        Print the provided arguments to the console.
        Args:
            args: List of positional arguments.
            kwargs: Dictionary of keyword arguments (flags).
        Returns:
            int: Exit code, 0 for success.
        """
        verbose = kwargs.get("verbose", False)
        get_logger("echo").info(f"Executing echo with args: {args}, kwargs: {kwargs}")
        if verbose:
            print(f"Echoing: {args}")
        else:
            print(" ".join(map(str, args)))
        return 0

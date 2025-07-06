import random
from core.core_types.command import BaseCommand
from core.logger import get_logger


class HeadsOrTails(BaseCommand):
    """
    Heads or Tails command that simulates a coin flip.
    """

    author = "Lunafy"
    date_created = "2025-06-17"
    description = "Simulate a coin flip"
    help = "Usage: echo <message> [options]"
    fun = True

    def execute(self, *args, **kwargs):
        """
        Print the provided arguments to the console.
        Args:
            args: List of positional arguments.
            kwargs: Dictionary of keyword arguments (flags).
        Returns:
            int: Exit code, 0 for success.
        """
        choice = random.choice(["Heads", "Tails"])
        print(f"The coin landed on: {choice}")
        get_logger("headsortails").info(f"Coin flip result: {choice}")
        return 0

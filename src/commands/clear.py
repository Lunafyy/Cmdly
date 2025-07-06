import os
from core.core_types.command import BaseCommand
from core.utils import Utils
from core.logger import get_logger


class Clear(BaseCommand):
    """
    Clear command that clears the console screen.
    """

    author = "Lunafy"
    date_created = "2025-06-17"
    description = "Clears the console screen."
    help = "Usage: clear"
    fun = False

    def execute(self, *args, **kwargs):
        """
        Clear the terminal screen.
        Returns:
            int: Exit code, 0 for success.
        """
        # Windows uses 'cls', Unix uses 'clear'
        command = "cls" if os.name == "nt" else "clear"
        os.system(command)
        get_logger("clear").info("Console cleared successfully.")

        Utils.welcome_message()

        return 0

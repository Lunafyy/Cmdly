from art import tprint

class Utils:
    """A utility class for the Cmdly application, providing static helper methods such as displaying the welcome message."""
    @staticmethod
    def welcome_message():
        """
        Displays a stylized welcome message for the Cmdly application, including instructions for accessing help or exiting.
        """
        tprint("Cmdly")
        print("Welcome to Cmdly! Type 'help' for a list of commands or 'exit' to quit.\n")
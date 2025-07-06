from typing import List, Dict, Any

class BaseCommand:
    # Metadata
    author: str = "Unknown"
    date_created: str = "Unknown"
    description: str = "No description provided"
    help: str = "No help available"

    def __init__(self):
        pass

    def execute(self, args: List[str], kwargs: Dict[str, Any]) -> int:
        """
        Override this method in subclasses.
        Args:
            args: positional arguments list
            kwargs: keyword arguments dict (flags and parameters)
        Returns:
            int: exit code, 0 for success
        """
        raise NotImplementedError("Execute method not implemented")


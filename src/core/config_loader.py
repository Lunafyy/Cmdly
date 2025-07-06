import json
import os


class Config:
    @staticmethod
    def get_config():
        """
        Loads and returns the configuration settings from the default_settings.json file.

        The function determines the path to the configuration file relative to the current file's location,
        opens the JSON file, and parses its contents into a Python dictionary.

        Returns:
            dict: The configuration settings loaded from the JSON file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "..", "config", "default_settings.json")
        config_path = os.path.normpath(config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

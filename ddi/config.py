import json
from os import path
import shutil

CONFIG_FILE = "config.json"
CONFIG_EXAMPLE_FILE = "config.json.example"

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass

def load_config():
    """Loads the configuration from config.json, creating it from example if not found."""
    if not path.exists(CONFIG_FILE):
        if path.exists(CONFIG_EXAMPLE_FILE):
            print(f"'{CONFIG_FILE}' not found. Creating it from '{CONFIG_EXAMPLE_FILE}'.")
            shutil.copy(CONFIG_EXAMPLE_FILE, CONFIG_FILE)
        else:
            raise ConfigurationError(
                f"Neither '{CONFIG_FILE}' nor '{CONFIG_EXAMPLE_FILE}' found.\n"
                "Please ensure 'config.json.example' exists in the project root."
            )

    with open(CONFIG_FILE, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Error decoding JSON from '{CONFIG_FILE}': {e}\n"
                "Please check the syntax of your config.json file."
            )
    return config

def get_config_value(config, key, default=None):
    """
    Safely gets a value from the config dictionary.
    Example: get_config_value(config, "infoblox.username")
    """
    keys = key.split('.')
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value

def save_config(config):
    """Saves the configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


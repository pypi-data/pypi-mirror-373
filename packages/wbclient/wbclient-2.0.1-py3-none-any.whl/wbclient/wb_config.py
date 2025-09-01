from os import environ as env
from pathlib import Path
import appdirs
import json
import logging


def get_config_path():
    # Use appdirs to get a user-friendly config directory
    # Example: ~/.config/my-app/ on Linux, %APPDATA%\my-app\ on Windows
    config_dir = Path(appdirs.user_config_dir("wbclient"))
    # Or, use a custom path like /home/user/wb/configuration
    # config_dir = Path.home() / "wb" / "configuration"
    config_file = config_dir / "wb_config.json"
    return config_dir, config_file


def load_global_config():
    """
    Reads a configuration JSON file, returns it as a dict, and loads the values into environment variables.
    :return: None
    """
    config_dir, config_file = get_config_path()

    # If config file doesn't exist, copy the default from the package
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        # Get the default config from the package
        default_config = {
            "serverid": "fms01",
            "host_name": "fms.mydomain.example",
            "use_ssl": True,
            "port": 443,
            "database_name": "whistleblower",
            "configuration_layout": "wb_configurations",
            "post_layout": "wb_post",
            "command_layout": "wb_commands",
            "post_script": "process data",
            "password": "••••••",
            "post_interval": 60,
            "keyboard_control": False,
            "command_user": "fmserver",
            "command_whitelist": [{"command": "/usr/sbin/reboot"}, {"command": "whoami"}, {"command": "ifconfig"}]
        }
        # Copy to user config directory
        with config_file.open("w") as dst:
            dst.write(json.dumps(default_config))
            dst.close()
        print(f"Created default config at {config_file}")
    try:
        with open(config_file, "r") as config_file:
            logging.info(f"Loading configuration from file: {config_file.name}")
            try:
                config_data = json.load(config_file)
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON configuration: {e}")
                return False
            prefix = 'https://'
            if not config_data['host_name'].startswith(prefix):
                config_data['host_name'] = prefix + config_data['host_name']
            if 'port' in config_data and config_data['port'] == "":
                config_data['port'] = 443  # set to default value
            logging.debug(config_data)
            # IJE: Iterate over the dictionary and set environment variables
            for key, value in config_data.items():
                env[key] = str(value)
            return True
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {e}")
        return False
    except Exception as e:
        logging.error(f"An error occurred while loading the configuration file: {e}")
        return False

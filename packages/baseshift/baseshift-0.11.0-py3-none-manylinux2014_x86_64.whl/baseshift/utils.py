import argparse
import json
import os
import re
import uuid
from pathlib import Path

CONFIG_DIR_NAME = ".baseshift"
CONFIG_FILE_NAME = "config"

# Global cache for the loaded configuration to avoid repeated file I/O
_config_cache = None


def load_config():
    """Loads the configuration from ~/.baseshift/config.

    Returns:
        dict: The loaded configuration data, or an empty dict if not found or error.
    """
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    home_dir = Path.home()
    config_file_path = home_dir / CONFIG_DIR_NAME / CONFIG_FILE_NAME
    if config_file_path.exists():
        try:
            with open(config_file_path, "r") as f:
                _config_cache = json.load(f)
                return _config_cache
        except json.JSONDecodeError:
            # Handle cases where the config file is corrupted
            _config_cache = {}
            return _config_cache  # Or raise an error/log a warning
        except Exception:
            _config_cache = {}
            return _config_cache  # Or raise an error/log a warning
    _config_cache = {}
    return _config_cache


def get_config_value(
    cli_arg_value, env_var_name, config_key, required=False, default=None
):
    """Resolves a configuration value with precedence: CLI > Env Var > Config File.

    Args:
        cli_arg_value: The value provided via CLI argument.
        env_var_name (str): The name of the environment variable (e.g., BASESHIFT_ORG_TOKEN).
        config_key (str): The key for the value in the config file (e.g., orgToken).
        required (bool, optional): If True and no value is found, raises ValueError. Defaults to False.
        default (any, optional): Default value to return if not found and not required. Defaults to None.

    Returns:
        The resolved configuration value.

    Raises:
        ValueError: If the value is required and not found through any means.
    """
    # 1. CLI argument
    if cli_arg_value is not None:
        return cli_arg_value

    # 2. Environment variable
    env_value = os.environ.get(env_var_name)
    if env_value is not None:
        return env_value

    # 3. Config file
    config_data = load_config()
    if config_key in config_data and config_data[config_key]:
        return config_data[config_key]

    if required:
        raise ValueError(
            f"{config_key} is required. Please provide it via CLI argument, "
            f"environment variable '{env_var_name}', or in the config file "
            f"at ~/.baseshift/config."
        )

    return default


def regex_type_uuid(
    arg_value,
    pat=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value")
    return arg_value


def parse_connection_string(conn_string, regex):
    match = re.search(regex, conn_string)
    return match.group(1) if match else ""


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def save_last_clone_uuid(clone_uuid: str):
    """Save the last started clone UUID to ~/.baseshift/config."""
    config_data = load_config()
    config_data["lastCloneUuid"] = clone_uuid

    # Save updated config
    home_dir = Path.home()
    config_dir = home_dir / CONFIG_DIR_NAME
    config_dir.mkdir(exist_ok=True)
    config_file_path = config_dir / CONFIG_FILE_NAME

    try:
        with open(config_file_path, "w") as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        # Don't fail the main operation if we can't save the last clone
        pass


def get_last_clone_uuid() -> str:
    """Get the last started clone UUID from ~/.baseshift/config, or None if not available."""
    config_data = load_config()
    return config_data.get("lastCloneUuid")

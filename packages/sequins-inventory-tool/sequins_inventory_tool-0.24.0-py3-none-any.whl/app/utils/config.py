"""Load and save user configuration data."""

from pathlib import Path
from typing import Any, Dict, Optional

from platformdirs import user_config_path
import tomlkit
from tomlkit import exceptions

from app.console import get_console
from app.constants import PACKAGE_AUTHOR, PACKAGE_NAME
from app.enums import Profile

CONFIG_FILE_NAME = 'config.toml'


def get_config_dir() -> Path:
    """Returns the directory where user configuration files are stored."""
    return user_config_path(
        appname=PACKAGE_NAME, appauthor=PACKAGE_AUTHOR, ensure_exists=True
    )


def get_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME


def load_config() -> Dict[str, Any]:
    """Loads the configuration from the local config file."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}  # Return empty dict if file doesn't exist

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return tomlkit.parse(f.read())
    except (OSError, exceptions.TOMLKitError) as e:
        get_console().print(
            f'Warning: Could not load config file {config_path}. Error: {e}'
        )
        return {}


def save_config(config_data: Dict[str, Any]):
    """Saves the given configuration data to the local config file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(config_data))
    except (OSError, exceptions.TOMLKitError) as e:
        get_console().print(
            f'Error: Could not save config file {config_path}. Error: {e}'
        )


def get_api_key(profile: Profile = Profile.PRODUCTION) -> Optional[str]:
    """
    Retrieves the API key from the loaded configuration for the given profile.
    """
    config = load_config()
    # First, try to get the key from the profile-specific section
    api_key = config.get(profile.value, {}).get('api_key')
    if api_key:
        return api_key

    # For backward compatibility, check the old location
    if profile == Profile.PRODUCTION:
        return config.get('api', {}).get('key')

    return None


def set_api_key_in_config(api_key: str, profile: Profile = Profile.PRODUCTION):
    """Saves the API key to the configuration file for the given profile."""
    config = load_config()
    if profile.value not in config:
        config[profile.value] = tomlkit.table()
    config[profile.value]['api_key'] = api_key
    save_config(config)


def get_api_endpoint(profile: Profile = Profile.PRODUCTION) -> Optional[str]:
    """
    Retrieves the API endpoint from the loaded configuration for the given
    profile.
    """
    config = load_config()
    return config.get(profile.value, {}).get('api_endpoint')


def set_api_endpoint_in_config(
    api_endpoint: str, profile: Profile = Profile.PRODUCTION
):
    """
    Saves the API endpoint to the configuration file for the given profile.
    """
    config = load_config()
    if profile.value not in config:
        config[profile.value] = tomlkit.table()
    config[profile.value]['api_endpoint'] = api_endpoint
    save_config(config)

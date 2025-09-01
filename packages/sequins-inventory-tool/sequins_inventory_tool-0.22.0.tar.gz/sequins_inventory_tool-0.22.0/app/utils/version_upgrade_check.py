"""Check if the current version is the latest and prompt for upgrade if not."""

import datetime
import importlib.metadata
import json
import os
from typing import Optional

from packaging.version import Version, parse as parse_version
from platformdirs import user_cache_dir
import requests
from rich.text import Text

from app.console import get_console
from app.constants import PACKAGE_AUTHOR, PACKAGE_NAME

# Define the interval for checking for updates (e.g., 24 hours)
CHECK_INTERVAL_SECONDS = 24 * 60 * 60


def _get_cache_file_path() -> str:
    """Gets the path for the version check cache file."""
    cache_dir = user_cache_dir(
        appname=PACKAGE_NAME, appauthor=PACKAGE_AUTHOR, ensure_exists=True
    )
    return os.path.join(cache_dir, 'version_check.json')


def _should_check_now(interval: int = CHECK_INTERVAL_SECONDS) -> bool:
    """Determines if a new version check is needed based on cache."""
    # Do not check when testing
    if os.getenv('SKIP_UPGRADE_CHECK') == '1':
        return False

    cache_file = _get_cache_file_path()
    if not os.path.exists(cache_file):
        return True

    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        last_check_timestamp = cache_data.get('last_check_timestamp')
        if last_check_timestamp:
            last_check_time = datetime.datetime.fromtimestamp(
                last_check_timestamp
            )
            time_since_last_check = datetime.datetime.now() - last_check_time
            if time_since_last_check.total_seconds() < interval:
                return False  # Too soon to check again
    except (json.JSONDecodeError, KeyError, TypeError):
        return True

    return True


def _update_cache(latest_version: str):
    """Updates the version check cache file."""
    cache_file = _get_cache_file_path()
    cache_data = {
        'last_check_timestamp': datetime.datetime.now().timestamp(),
        'latest_version': latest_version,
    }
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    except IOError as e:
        get_console().print(
            f'[bold red]Error: Could not write to version check cache file: '
            f'{e}[/bold red]'
        )


def get_current_app_version() -> Optional[Version]:
    """Retrieves the version of the currently installed package."""
    try:
        version_str = importlib.metadata.version(PACKAGE_NAME)
        return parse_version(version_str)
    except importlib.metadata.PackageNotFoundError:
        get_console().print(
            f'[bold yellow]Warning: Package "{PACKAGE_NAME}" not found in '
            f'environment. Cannot determine current version.[/bold yellow]'
        )
        return None
    except Exception as e:
        get_console().print(
            f'[bold red]Error parsing current version for '
            f'"{PACKAGE_NAME}": {e}[/bold red]'
        )
        return None


def _get_latest_pypi_version() -> Optional[Version]:
    """Fetches the latest package version from PyPI."""
    pypi_url = f'https://pypi.org/pypi/{PACKAGE_NAME}/json'
    try:
        response = requests.get(pypi_url, timeout=5)
        response.raise_for_status()
        data = response.json()

        latest_version_str = data['info']['version']

        return parse_version(latest_version_str)
    except requests.exceptions.RequestException as e:
        get_console().print(
            f'[bold yellow]Warning: Could not check for new version '
            f'(network error): {e}[/bold yellow]'
        )
        return None
    except (KeyError, ValueError) as e:
        get_console().print(
            f'[bold yellow]Warning: Could not parse PyPI data for '
            f'{PACKAGE_NAME}: {e}[/bold red]'
        )
        return None


def check_for_new_version_and_notify(
    check_interval_seconds: Optional[int] = None,
):
    """Checks for a new version of the package on PyPI and notifies the user
    if available.

    Uses a simple file-based cache to avoid frequent API calls.
    """
    current_version = get_current_app_version()
    if not current_version:
        return  # Already warned if version couldn't be determined

    # Use the provided interval or the default
    effective_check_interval = (
        check_interval_seconds
        if check_interval_seconds is not None
        else CHECK_INTERVAL_SECONDS
    )

    if not _should_check_now(effective_check_interval):
        return  # Too soon to check again, skip network call

    latest_version = _get_latest_pypi_version()
    if not latest_version:
        return  # Failed to get latest version, warning already printed

    # Update cache with the latest version found, so we don't check again
    # too soon
    _update_cache(str(latest_version))

    if latest_version > current_version:
        get_console().print(
            Text.assemble(
                Text('🚀 A new version of ', style='bold green'),
                Text(PACKAGE_NAME, style='bold magenta'),
                Text(' is available: ', style='bold green'),
                Text(f'{latest_version}', style='bold cyan'),
                Text(f' (You are on {current_version})', style='dim'),
                Text('\n   Consider upgrading with: ', style='green'),
                Text(f'pipx upgrade {PACKAGE_NAME}', style='bold yellow'),
                Text('\n', style='green'),
            )
        )
    elif latest_version < current_version:
        get_console().print(
            f'[bold yellow]Warning: Your local version ({current_version}) is '
            f'newer than the latest stable on PyPI ({latest_version}).'
            '[/bold yellow]'
        )

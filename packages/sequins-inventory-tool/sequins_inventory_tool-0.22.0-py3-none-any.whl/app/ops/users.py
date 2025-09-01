"""Command to interact with the users endpoint."""

import json
import logging
from typing import Optional
import urllib.parse

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.response_utils import handle_response

logger = logging.getLogger(__name__)

user_commands = typer.Typer()


def create_table() -> Table:
    """Create a table for displaying user information."""
    table = Table(title='Users')
    table.add_column('Username', justify='left')
    table.add_column('Enabled')
    table.add_column('Roles')
    table.add_column('Permissions')
    return table


def get_roles_from_string(roles: Optional[str]) -> list[str]:
    """Convert a comma-separated string of roles into a list."""
    return [role.strip() for role in roles.split(',')] if roles else []


def get_permissions_from_string(permissions: Optional[str]) -> dict[str, bool]:
    """Convert a comma-separated string of permissions into a dictionary."""
    applicable_permissions = {}
    pairs = permissions.split(',') if permissions else []
    for pair in pairs:
        if '=' not in pair or pair.count('=') != 1:
            logger.warning('Invalid permission format: %s. Skipping.', pair)
            continue
        key, value = pair.split('=')
        applicable_permissions[key.strip()] = value.strip().lower() == 'true'
    return applicable_permissions


@user_commands.command(name='display')
@require_api_endpoint_and_key()
def print_users(ctx: typer.Context):
    """Fetch and display all users in the database.

    Note that you require the `admin` role to access this command.
    """
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}'
    headers = {API_KEY_NAME: api_key}

    # Need to paginate through the users
    page = 1
    size = 50
    users = []
    while True:
        response = requests.get(
            user_url, headers=headers, params={'page': page, 'size': size}
        )
        handle_response(response)
        items = response.json()['items']
        users.extend(items)
        if len(items) < size:
            break
        page += 1

    if not users:
        console.print('No users found.')
        raise typer.Exit()

    table = create_table()

    for user in users:
        table.add_row(
            user['username'],
            str(user['enabled']),
            ', '.join(user['roles']),
            json.dumps(user['permissions']),
        )

    console.print(table)


@user_commands.command(name='current')
@require_api_endpoint_and_key()
def print_current(ctx: typer.Context):
    """Fetch and display information about the current user.

    The current user is determined by the API key used to authenticate.
    """
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}current/'
    headers = {API_KEY_NAME: api_key}

    response = requests.get(user_url, headers=headers)
    handle_response(response)
    user = response.json()

    if not user:
        console.print('User not found.')
        raise typer.Exit()

    table = create_table()

    table.add_row(
        user['username'],
        str(user['enabled']),
        ', '.join(user['roles']),
        json.dumps(user['permissions']),
    )

    console.print(table)


@user_commands.command(name='create')
@require_api_endpoint_and_key()
def create_user(
    ctx: typer.Context,
    username: str = typer.Argument(..., help='Username of the new user'),
    roles: Annotated[
        Optional[str], typer.Option(help='Comma separated roles for the user')
    ] = None,
    permissions: Annotated[
        Optional[str],
        typer.Option(help='Comma separated permissions for the user'),
    ] = None,
):
    """Create a new user in the database.

    This command requires the `admin` role to execute.
    """
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}'
    headers = {API_KEY_NAME: api_key}

    applicable_roles = get_roles_from_string(roles)
    applicable_permissions = get_permissions_from_string(permissions)

    payload = {
        'username': username,
        'enabled': True,  # Default to enabled
        'roles': applicable_roles,
        'permissions': applicable_permissions,
    }

    response = requests.post(user_url, headers=headers, json=payload)
    handle_response(response)

    console.print(f'User {username} created successfully.')


def change_user_enabled(enabled: bool, username: str, ctx: typer.Context):
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}'
    headers = {API_KEY_NAME: api_key}
    payload = {'username': username, 'enabled': enabled}
    response = requests.patch(user_url, headers=headers, json=payload)
    handle_response(response)
    state = 'enabled' if enabled else 'disabled'
    console.print(f'User {username} {state} successfully.')


@user_commands.command(name='enable')
@require_api_endpoint_and_key()
def enable_user(
    ctx: typer.Context,
    username: str = typer.Argument(..., help='Username of the user to enable'),
):
    """Change the state of a user to enabled.

    This command requires the `admin` role to execute.
    """
    change_user_enabled(True, username, ctx)


@user_commands.command(name='disable')
@require_api_endpoint_and_key()
def disable_user(
    ctx: typer.Context,
    username: str = typer.Argument(..., help='Username of the user to disable'),
):
    """Change the state of a user to disabled.

    This command requires the `admin` role to execute.
    """
    change_user_enabled(False, username, ctx)


@user_commands.command(name='set-roles')
@require_api_endpoint_and_key()
def set_user_roles(
    ctx: typer.Context,
    username: str = typer.Argument(
        ..., help='Username of the user to update roles'
    ),
    roles: Annotated[
        Optional[str], typer.Option(help='Comma separated roles for the user')
    ] = None,
):
    """Set roles for a user in the database.

    This will overwrite any existing roles for the user. If you wish to add or
    remove roles,you will need to specify all the roles you want the user to
    have again.

    This command requires the `admin` role to execute.
    """
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}'
    headers = {API_KEY_NAME: api_key}

    applicable_roles = get_roles_from_string(roles)

    payload = {'username': username, 'roles': applicable_roles}
    response = requests.patch(user_url, headers=headers, json=payload)
    handle_response(response)
    console.print(
        f'Roles for user {username} updated successfully to: '
        f'{", ".join(response.json().get("roles", []))}'
    )


@user_commands.command(name='set-permissions')
@require_api_endpoint_and_key()
def set_user_permissions(
    ctx: typer.Context,
    username: str = typer.Argument(
        ..., help='Username of the user to update permissions'
    ),
    permissions: Annotated[
        Optional[str],
        typer.Option(help='Comma separated permissions for the user'),
    ] = None,
):
    """Set permissions for the user in the database.

    This will overwrite any existing permissions for the user. If you wish to
    add or remove permissions, you will need to specify all the permissions you
    want the user to have again.

    This command requires the `admin` role to execute
    """
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}'
    headers = {API_KEY_NAME: api_key}

    applicable_permissions = get_permissions_from_string(permissions)
    if not applicable_permissions:
        console.print('No valid permissions provided.')
        raise typer.Exit(code=1)

    payload = {
        'username': username,
        'permissions': applicable_permissions,
    }
    response = requests.patch(user_url, headers=headers, json=payload)
    handle_response(response)
    console.print(
        f'Permissions for user {username} updated successfully to: '
        f'{json.dumps(response.json().get("permissions", {}))}'
    )


@user_commands.command(name='generate-api-key')
@require_api_endpoint_and_key()
def generate_api_key(
    ctx: typer.Context,
    username: Annotated[
        str, typer.Argument(help='Username for which to generate the API key')
    ],
):
    """Generate and return a new API key for the given user."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    user_url = f'{api_endpoint}{ApiPaths.USERS}'
    headers = {API_KEY_NAME: api_key}

    # Ensure the username is URL-encoded to handle special characters
    username = urllib.parse.quote(username)
    response = requests.patch(
        f'{user_url}generate-api-key/{username}', headers=headers
    )
    handle_response(response)

    console.print(
        f'New API key generated successfully: {response.json().get("api_key")}'
    )

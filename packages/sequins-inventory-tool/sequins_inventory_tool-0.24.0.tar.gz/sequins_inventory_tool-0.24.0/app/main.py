"""Inventory tool CLI entry point."""

import logging
import os

from dotenv import load_dotenv
import typer

from app.enums import Profile
from app.ops.audit import audit_app
from app.ops.azenta import azenta_app
from app.ops.box import box_commands
from app.ops.database import app as database_app
from app.ops.location import location_commands
from app.ops.order import order_commands
from app.ops.parts import parts_app
from app.ops.product_numbering import product_naming_app
from app.ops.users import user_commands
from app.ops.variant import variant_commands
from app.utils.config import (
    get_api_endpoint,
    get_api_key,
    set_api_endpoint_in_config,
    set_api_key_in_config,
)
from app.utils.version_upgrade_check import (
    check_for_new_version_and_notify,
    get_current_app_version,
)

logger = logging.getLogger(__name__)

load_dotenv('.env')

DEFAULT_ENDPOINTS = {
    Profile.PRODUCTION: 'https://inventory-api.corp.sequins.bio',
    Profile.STAGING: 'https://inventory-api-staging.corp.sequins.bio',
    Profile.DEV: 'https://inventory-api-dev.corp.sequins.bio',
    Profile.LOCAL: 'http://localhost:8100',
}

app = typer.Typer()
app.add_typer(audit_app, name='audit', help='Display access audit logs.')
app.add_typer(
    azenta_app, name='azenta', help='Upload data from Azenta to the database.'
)
app.add_typer(box_commands, name='box', help='Manage boxes.')
app.add_typer(
    database_app,
    name='database',
    help='Interact directly with the underlying database.',
)
app.add_typer(
    location_commands, name='location', help='Manage location operations.'
)
app.add_typer(order_commands, name='order', help='Manage order operations.')
app.add_typer(parts_app, name='part', help='Manage part operations.')
app.add_typer(
    product_naming_app,
    name='product-numbering',
    help='Manage product numbering operations.',
)
app.add_typer(user_commands, name='user', help='Manage user operations.')
app.add_typer(
    variant_commands, name='variant', help='Manage variant operations.'
)


# Callback is called before executing every command, to allow us to set global
# state.
@app.callback()
def global_callback(
    ctx: typer.Context,
    profile: Profile = typer.Option(
        Profile.PRODUCTION,
        '--profile',
        help='The profile to use for configuration.',
        case_sensitive=False,
    ),
    debug: bool = typer.Option(False, '--debug', help='Enable debug logging'),
    api_endpoint: str = typer.Option(
        None, '--api-endpoint', help='Address of API endpoint.'
    ),
    api_key: str = typer.Option(
        None, '--api-key', help='API key for authentication.'
    ),
    database_server_name: str = typer.Option(
        None, '--database-server-name', help='MongoDB server name'
    ),
    database_name: str = typer.Option(
        None, '--database-name', help='MongoDB database name.'
    ),
):
    """Global callback to set the logging level."""

    final_api_endpoint = (
        api_endpoint
        or os.getenv('API_ENDPOINT')
        or get_api_endpoint(profile)
        or DEFAULT_ENDPOINTS.get(profile)
    )
    final_api_key = api_key or os.getenv('API_KEY') or get_api_key(profile)
    final_database_server_name = (
        database_server_name or os.getenv('DATABASE_SERVER_NAME') or ''
    )
    final_database_name = database_name or os.getenv('DATABASE_NAME') or ''

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger.debug(f'Using profile: {profile.value}')
    logger.debug(f'API endpoint: {final_api_endpoint}')
    logger.debug(f'API key: {final_api_key}')

    ctx.obj = {
        'profile': profile,
        'api_endpoint': final_api_endpoint,
        'api_key': final_api_key,
        'database_server_name': final_database_server_name,
        'database_name': final_database_name,
    }

    check_for_new_version_and_notify()


@app.command(
    name='set-api-key', help='Save your API key to a local config file.'
)
def set_api_key(
    ctx: typer.Context,
    api_key: str = typer.Argument(..., help='The API key to save.'),
):
    """
    Saves the provided API key to a local configuration file.
    This key will be used by default for commands that require authentication.
    """
    profile: Profile = ctx.obj['profile']
    set_api_key_in_config(api_key, profile)

    typer.echo(f'API key successfully saved for profile: {profile.value}')
    typer.echo('This key will be used by default for authenticated commands.')


@app.command(
    name='set-api-endpoint',
    help='Save your API endpoint to a local config file.',
)
def set_api_endpoint(
    ctx: typer.Context,
    api_endpoint: str = typer.Argument(..., help='The API endpoint to save.'),
):
    """
    Saves the provided API endpoint to a local configuration file.
    This endpoint will be used by default for commands that require
    authentication.
    """
    profile: Profile = ctx.obj['profile']
    set_api_endpoint_in_config(api_endpoint, profile)

    typer.echo(f'API endpoint successfully saved for profile: {profile.value}')
    typer.echo(
        'This endpoint will be used by default for authenticated commands.'
    )


@app.command(
    name='version', help='Display the current version of the application.'
)
def version():
    """Display the current version of the application."""
    current_version = get_current_app_version()
    if current_version:
        typer.echo(f'Current app version: {current_version}')
    else:
        typer.echo('Could not determine the current app version.')


if __name__ == '__main__':
    app()

"""CLI to manipulate users directly in the database."""

import hashlib
import logging
import os
from typing import Optional
import uuid

from cryptography.fernet import Fernet
import pymongo
from pymongo import errors
import typer
from typing_extensions import Annotated

from app.console import get_console

logger = logging.getLogger(__name__)

app = typer.Typer()

USER_COLLECTION = 'users'


@app.command(name='create')
def create_user(
    ctx: typer.Context,
    username: Annotated[str, typer.Argument(help='Username for the API key')],
    api_key: Annotated[
        Optional[str], typer.Option(help='API key to use')
    ] = None,
    roles: Annotated[
        Optional[str], typer.Option(help='Comma separated roles for the user')
    ] = None,
    permissions: Annotated[
        Optional[str],
        typer.Option(help='Comma separated permissions for the user'),
    ] = None,
    api_signing_key: Annotated[
        str, typer.Option(help='API key signing key')
    ] = os.getenv('API_KEY_SIGNING_KEY', ''),
) -> None:
    """Create an API key."""
    console = get_console()
    console.log(f'Creating user {username}')

    server = ctx.obj['database_server_name']
    database = ctx.obj['database_name']

    if not server or not database:
        console.log(
            'Database server name and database name must be set via CLI '
            'or .env file.'
        )
        raise typer.Exit(1)

    client = pymongo.MongoClient(server)
    db = client[database]
    collection = db[USER_COLLECTION]

    calc_api_key = None
    api_key_hash = None

    if api_key:
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        if api_signing_key:
            f = Fernet(api_signing_key.encode())
            calc_api_key = f.encrypt(api_key.encode()).decode()
        else:
            calc_api_key = api_key

    applicable_roles = (
        [role.strip() for role in roles.split(',')] if roles else []
    )

    applicable_permissions = {}
    pairs = permissions.split(',') if permissions else []
    for pair in pairs:
        if '=' not in pair or pair.count('=') != 1:
            logger.warning('Invalid permission format: %s. Skipping.', pair)
            continue
        key, value = pair.split('=')
        applicable_permissions[key.strip()] = value.strip().lower() == 'true'

    console.log(
        f'Creating user {username} with API key {api_key}, '
        f'roles {applicable_roles}, permissions {applicable_permissions}',
    )

    user = {
        'username': username,
        'enabled': True,
        'roles': applicable_roles,
        'permissions': applicable_permissions,
        '_id': uuid.uuid4().hex,
    }

    if calc_api_key:
        user['api_key'] = calc_api_key
    if api_key_hash:
        user['api_key_hash'] = api_key_hash

    try:
        collection.insert_one(user)
        console.log(
            f'User {username} created with roles {applicable_roles} '
            f'and permissions {applicable_permissions}'
            f'{" and API key: " + calc_api_key if calc_api_key else "None"}'
        )
    except errors.DuplicateKeyError:
        console.log(f'User {username} already exists - try update instead.')

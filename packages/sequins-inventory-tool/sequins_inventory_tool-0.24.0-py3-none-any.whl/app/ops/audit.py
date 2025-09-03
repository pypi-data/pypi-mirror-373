"""CLI tool for showing audit logs."""

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, API_REQUEST_TIMEOUT_SEC, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.response_utils import handle_response

audit_app = typer.Typer()

DEFAULT_PAGE_SIZE = 50


@audit_app.command(name='display', help='Display audit logs')
@require_api_endpoint_and_key()
def display_audit_logs(
    ctx: typer.Context,
    count: Annotated[
        int,
        typer.Option(
            '--count', '-c', help='Number of logs to display', show_default=True
        ),
    ] = 50,
    username: Annotated[
        str | None, typer.Option('--username', '-u', help='Filter by username')
    ] = None,
    method: Annotated[
        str | None, typer.Option('--method', '-m', help='Filter by HTTP method')
    ] = None,
    path: Annotated[
        str | None, typer.Option('--path', '-p', help='Filter by request path')
    ] = None,
):
    """Display audit logs with pagination."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    audit_url = f'{api_endpoint}{ApiPaths.ACCESS_AUDIT_LOGS}'
    headers = {API_KEY_NAME: api_key}

    # By default we want the most recent logs first
    filter_options = {'sortOrder': 'desc'}
    if username:
        filter_options['username'] = username
    if method:
        filter_options['method'] = method
    if path:
        filter_options['path'] = path

    page = 1
    size = count if count < DEFAULT_PAGE_SIZE else DEFAULT_PAGE_SIZE
    items = []
    while True:
        response = requests.get(
            audit_url,
            headers=headers,
            params={'page': page, 'size': size} | filter_options,
            timeout=API_REQUEST_TIMEOUT_SEC,
        )
        handle_response(response)

        audit_data = response.json()
        items.extend(audit_data.get('items', []))

        if not audit_data.get('pages') or page >= audit_data['pages']:
            break

        # If we have enough items, we can stop fetching more
        if len(items) >= count:
            break

        page += 1

    console = get_console()

    if not items:
        console.print('No audit logs found.')
        return

    table = Table(title='Audit Logs')
    table.add_column('Username', justify='center')
    table.add_column('Method', justify='left')
    table.add_column('Path', justify='left')
    table.add_column('Client IP', justify='right')
    table.add_column('Timestamp', justify='right')

    for item in items:
        created_at = item.get('created_at_utc')
        timestamp = format_utc_to_local(created_at) if created_at else 'N/A'
        table.add_row(
            item.get('username', 'N/A'),
            item.get('method', 'N/A'),
            item.get('path', 'N/A'),
            item.get('client_ip', 'N/A'),
            timestamp,
        )

    console.print(table)

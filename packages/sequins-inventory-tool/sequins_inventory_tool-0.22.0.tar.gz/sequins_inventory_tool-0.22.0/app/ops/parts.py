"""CLI for interacting with the parts database."""

from datetime import datetime, timezone
import logging
from typing import Optional

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.response_utils import handle_response

logger = logging.getLogger(__name__)

parts_app = typer.Typer()


def _format_date_utc_or_none(date_str: str | None) -> str:
    """Format a date string or return an empty string if None."""
    if date_str:
        return format_utc_to_local(date_str)
    return ''


def _set_date_to_end_of_day(date_str: str) -> str:
    """Set the date to the end of the day for the given YYYY-MM-DD string.

    Args:
        date_str (str): A date string in the format 'YYYY-MM-DD'.

    Returns:
        str: The ISO 8601 formatted string representing the date at 23:59:59
        UTC.

    Raises:
        ValueError: If the input string does not match the 'YYYY-MM-DD' format.
    """
    date_dt = datetime.strptime(date_str, '%Y-%m-%d').replace(
        hour=23, minute=59, second=59
    )
    return date_dt.replace(tzinfo=timezone.utc).isoformat()


def create_table(verbose: bool, archived: bool = False) -> Table:
    """Create a table for displaying part information."""
    table = Table(title='Parts')
    table.add_column('Part Key', justify='left')
    table.add_column('Part Number', justify='left')
    table.add_column('Lot Number')
    table.add_column('Constituent Lot Numbers')
    table.add_column('Manufactured At', justify='left')
    table.add_column('Expires At', justify='left')
    if archived:
        table.add_column('Archived', justify='left')
    if verbose:
        table.add_column('Created By')
        table.add_column('Created At')
        table.add_column('Updated By')
        table.add_column('Updated At')
    return table


def add_part_to_table(
    table: Table, part: dict, archived=False, verbose=False
) -> None:
    """Add a part dictionary to the table."""
    row_data = [
        part['_id'],
        part['part_number'],
        part['lot_number'],
        ','.join(sorted(part['constituent_lot_numbers'])),
        _format_date_utc_or_none(part.get('manufactured_at_utc')),
        _format_date_utc_or_none(part.get('expires_at_utc')),
    ]
    if archived:
        row_data.append(str(part.get('archived', False)))
    if verbose:
        row_data.extend(
            [
                part.get('created_by') or 'N/A',
                format_utc_to_local(part['created_at_utc']),
                part.get('updated_by') or 'N/A',
                format_utc_to_local(part['updated_at_utc']),
            ]
        )
    table.add_row(*row_data)


def parse_constituent_lot_numbers(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(',')]


@parts_app.command(name='display')
@require_api_endpoint_and_key()
def display_parts(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
    archived: Annotated[
        bool,
        typer.Option(
            '--archived',
            help='Include archived parts in the display',
        ),
    ] = False,
):
    """Display a table of parts in the database."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']
    console = get_console()

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    headers = {API_KEY_NAME: api_key}

    filters = {
        'archived': archived,
    }

    filters_query = {k: v for k, v in filters.items() if v is not None}
    page = 1
    size = 50
    parts = []
    while True:
        result = requests.get(
            parts_url,
            headers=headers,
            params={'page': page, 'size': size} | filters_query,
        )
        handle_response(result)
        data = result.json()
        items = data.get('items', [])
        parts.extend(items)
        if len(items) < size:
            break
        page += 1

    if not parts:
        console.print('No parts found.')
        raise typer.Exit()

    table = create_table(verbose=verbose, archived=archived)
    for part in parts:
        add_part_to_table(table, part, archived=archived, verbose=verbose)

    console.print(table)


@parts_app.command(name='create')
@require_api_endpoint_and_key()
def create_part(
    ctx: typer.Context,
    part_number: Annotated[str, typer.Option(help='Part number')],
    constituent_lot_numbers: Annotated[
        str,
        typer.Option(help='Comma separated list of constituent lot numbers'),
    ],
    manufactured_at: Annotated[
        Optional[str],
        typer.Option(help='Manufacturing date in YYYY-MM-DD format (optional)'),
    ] = None,
    expires_at: Annotated[
        Optional[str],
        typer.Option(help='Expiration date in YYYY-MM-DD format (optional)'),
    ] = None,
):
    """Create a part in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    console = get_console()

    if not part_number:
        console.print('Part number is required.')
        raise typer.Exit(code=1)

    if not constituent_lot_numbers:
        console.print('Constituent lot numbers are required.')
        raise typer.Exit(code=1)

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    headers = {API_KEY_NAME: api_key}

    data = {
        'part_number': part_number,
        'constituent_lot_numbers': parse_constituent_lot_numbers(
            constituent_lot_numbers
        ),
    }

    if manufactured_at:
        try:
            manufactured_at_utc = _set_date_to_end_of_day(manufactured_at)
            data['manufactured_at_utc'] = manufactured_at_utc
        except ValueError as e:
            console.print(f'Invalid manufacturing date format: {e}')
            raise typer.Exit(code=1)

    if expires_at:
        try:
            expires_at_utc = _set_date_to_end_of_day(expires_at)
            data['expires_at_utc'] = expires_at_utc
        except ValueError as e:
            console.print(f'Invalid expiration date format: {e}')
            raise typer.Exit(code=1)

    result = requests.post(parts_url, headers=headers, json=data)
    handle_response(result)
    part = result.json()

    console.log('Part created successfully.')

    table = create_table(verbose=True, archived=True)
    add_part_to_table(table, part, archived=True, verbose=True)
    console.print(table)


@parts_app.command(name='count')
@require_api_endpoint_and_key()
def count_parts(
    ctx: typer.Context,
    part_number: Annotated[
        Optional[str], typer.Option(help='Part number to filter by')
    ] = None,
    location: Annotated[
        Optional[str], typer.Option(help='Location to filter by')
    ] = None,
):
    """Count the number of parts in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}count'
    headers = {API_KEY_NAME: api_key}

    filter_params = {
        k: v
        for k, v in {'part_number': part_number, 'location': location}.items()
        if v is not None
    }

    result = requests.get(parts_url, headers=headers, params=filter_params)
    handle_response(result)
    data = result.json()

    table = Table(title='counts')
    table.add_column('Part Number', justify='left')
    table.add_column('Location')
    table.add_column('Available')
    table.add_column('Reserved')

    for item in data:
        part_number = item.get('part_number', '')
        for country, status_counts in item['count'].items():
            available = str(status_counts.get('Available', '0'))
            reserved = str(status_counts.get('Reserved', '0'))
            table.add_row(part_number, country, available, reserved)

    console = get_console()
    console.print(table)


@parts_app.command(name='update')
@require_api_endpoint_and_key()
def update_part(
    ctx: typer.Context,
    part_key: Annotated[str, typer.Argument(help='Part key to update')],
    lot_numbers: Annotated[
        Optional[str],
        typer.Option(
            help='Comma separated list of lot numbers to set (optional)'
        ),
    ] = None,
    manufactured_at: Annotated[
        Optional[str],
        typer.Option(help='Manufacturing date in YYYY-MM-DD format (optional)'),
    ] = None,
    expires_at: Annotated[
        Optional[str],
        typer.Option(help='Expiration date in YYYY-MM-DD format (optional)'),
    ] = None,
    archived: Annotated[
        Optional[bool],
        typer.Option(
            '--archived',
            help='Mark the part as archived',
        ),
    ] = None,
):
    """Update a part in the database."""
    api_endpoint: str = ctx.obj['api_endpoint']
    api_key: str = ctx.obj['api_key']

    url = f'{api_endpoint}{ApiPaths.PARTS}{part_key}'
    headers = {API_KEY_NAME: api_key}

    console = get_console()
    if (
        not lot_numbers
        and not manufactured_at
        and not expires_at
        and archived is None
    ):
        console.print('No fields to update.')
        raise typer.Exit(code=1)

    payload: dict[str, str | bool | list[str]] = {}
    if lot_numbers:
        payload['lot_numbers'] = parse_constituent_lot_numbers(lot_numbers)

    if manufactured_at:
        try:
            payload['manufactured_at_utc'] = _set_date_to_end_of_day(
                manufactured_at
            )
        except ValueError:
            console.print(f'Invalid manufacturing date: {manufactured_at}')
            raise typer.Exit(code=1)

    if expires_at:
        try:
            payload['expires_at_utc'] = _set_date_to_end_of_day(expires_at)
        except ValueError:
            console.print(f'Invalid expiration date: {expires_at}')
            raise typer.Exit(code=1)

    if archived is not None:
        payload['archived'] = archived

    result = requests.patch(url, headers=headers, json=payload)
    handle_response(result)

    console.log('Part updated successfully')
    part = result.json()

    table = create_table(verbose=True, archived=True)
    add_part_to_table(table, part, verbose=True, archived=True)
    console.print(table)

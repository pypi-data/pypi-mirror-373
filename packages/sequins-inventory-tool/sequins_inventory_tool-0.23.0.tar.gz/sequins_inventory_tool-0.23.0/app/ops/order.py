"""Command to interact with the orders endpoint."""

from __future__ import annotations

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, API_REQUEST_TIMEOUT_SEC, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.part_util import get_part_number_and_lot_from_part_key
from app.utils.response_utils import handle_response

order_commands = typer.Typer()


def format_items(items_list):
    """Format the items list as a comma-separated string of
    part_number:count.
    """
    return ', '.join(
        f'{item["part_number"]}:{item["count"]}'
        for item in items_list
        if 'part_number' in item and 'count' in item
    )


def _format_part_with_count(api_endpoint, api_key, item):
    """Helper to format a single item with part_key and count as
    part_number:lot_number:count.
    """
    part_number, lot_number = get_part_number_and_lot_from_part_key(
        api_endpoint, api_key, item['part_key']
    )
    return f'{part_number}:{lot_number}:{item["count"]}'


def format_parts_with_count_list(api_endpoint, api_key, items_list):
    """Format a list of items (like allocations or shipped parts) as a
    comma-separated string of part_number:lot_number:count.
    """
    return ', '.join(
        _format_part_with_count(api_endpoint, api_key, item)
        for item in items_list
        if 'part_key' in item and 'count' in item
    )


@order_commands.command(name='display')
@require_api_endpoint_and_key()
def print_orders(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Display all of the orders in the inventory."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    orders_url = f'{api_endpoint}{ApiPaths.ORDERS}'
    headers = {API_KEY_NAME: api_key}

    page = 1
    size = 50
    items = []

    while True:
        result = requests.get(
            orders_url,
            headers=headers,
            params={'page': page, 'size': size},
            timeout=API_REQUEST_TIMEOUT_SEC,
        )
        handle_response(result)
        data = result.json()
        current_items = data.get('items', [])
        items.extend(current_items)
        pages = data.get('pages', 1)
        if page >= pages:
            break
        page += 1

    console = get_console()

    if not items:
        console.print('No orders found.')
        raise typer.Exit(code=0)

    table = Table(title='Orders', show_lines=True, expand=True)
    table.add_column('Quote Reference', justify='left', no_wrap=True)
    table.add_column('Order Reference', justify='left', no_wrap=True)
    table.add_column('Invoice Reference', justify='left', no_wrap=True)
    table.add_column('Status', justify='left', no_wrap=True)
    table.add_column('Items', justify='left', no_wrap=True)
    table.add_column('Allocation', justify='left', no_wrap=True)
    table.add_column('Shipped Parts', justify='left', no_wrap=True)
    if verbose:
        table.add_column('Created By', justify='left')
        table.add_column('Created At', justify='left')
        table.add_column('Updated By', justify='left')
        table.add_column('Updated At', justify='left')

    for item in items:
        row_data = [
            item.get('quote_reference', ''),
            item.get('order_reference', ''),
            item.get('invoice_reference', ''),
            item.get('status', ''),
            format_items(item.get('items', [])),
            format_parts_with_count_list(
                api_endpoint, api_key, item.get('allocations', [])
            ),
            format_parts_with_count_list(
                api_endpoint, api_key, item.get('shipped_parts', [])
            ),
        ]
        if verbose:
            row_data.extend(
                [
                    item.get('created_by', ''),
                    format_utc_to_local(item['created_at_utc']),
                    item.get('updated_by', ''),
                    format_utc_to_local(item['updated_at_utc']),
                ]
            )
        table.add_row(*row_data)

    console.print(table)

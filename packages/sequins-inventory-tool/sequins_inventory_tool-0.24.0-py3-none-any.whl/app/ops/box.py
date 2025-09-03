"""CLI to interact with the box endpoint of the inventory API."""

from __future__ import annotations

from typing import List, Optional

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.part_util import (
    get_part_key_from_part_number_and_lot,
    get_part_number_and_lot_from_part_key,
)
from app.utils.response_utils import handle_response

box_commands = typer.Typer()

content_commands = typer.Typer()
box_commands.add_typer(content_commands, name='content')


@box_commands.command(name='display', help='Display all boxes in a location')
@require_api_endpoint_and_key()
def display_boxes(
    ctx: typer.Context,
    location_key: Annotated[
        Optional[str], typer.Option(help='Location key to filter boxes')
    ] = None,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Display boxes in a specific location."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    box_url = f'{api_endpoint}{ApiPaths.BOXES}'
    headers = {API_KEY_NAME: api_key}
    params = {'location_key': location_key} if location_key else {}

    page = 1
    size = 50
    items = []
    while True:
        response = requests.get(
            box_url,
            headers=headers,
            params={'page': page, 'size': size} | params,
        )
        handle_response(response)

        boxes_data = response.json()
        items.extend(boxes_data.get('items', []))
        pages = boxes_data.get('pages', 1)
        if page >= pages:
            break
        page += 1

    console = get_console()
    if not items:
        console.print('No boxes found for the specified location.')
        raise typer.Exit(code=0)

    table = Table(title='Boxes in Location')
    table.add_column('Name', justify='left')
    table.add_column('ID', justify='left')
    table.add_column('Location Key', justify='left')
    if verbose:
        table.add_column('Created By', justify='left')
        table.add_column('Created At', justify='left')
        table.add_column('Updated By', justify='left')
        table.add_column('Updated At', justify='left')

    for item in items:
        row_data = [
            item['name'],
            item['_id'],
            item['location_key'],
        ]
        if verbose:
            row_data.extend(
                [
                    item['created_by'],
                    format_utc_to_local(item['created_at_utc']),
                    item['updated_by'],
                    format_utc_to_local(item['updated_at_utc']),
                ]
            )
        table.add_row(*row_data)

    console.print(table)


@box_commands.command(name='create', help='Create a new box')
@require_api_endpoint_and_key()
def create_box(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help='Name of the new box')],
    location_key: Annotated[
        Optional[str], typer.Option(help='Location key for the new box')
    ] = None,
):
    """Create a new box."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    box_url = f'{api_endpoint}{ApiPaths.BOXES}'
    headers = {API_KEY_NAME: api_key}
    data = {
        'location_key': location_key,
        'name': name,
    }

    response = requests.post(box_url, headers=headers, json=data)
    handle_response(response)

    box_data = response.json()
    get_console().print(
        f'Created box: {box_data["name"]} (ID: {box_data["_id"]})'
    )


@box_commands.command(name='move', help='Move box to a new location')
@require_api_endpoint_and_key()
def move_box(
    ctx: typer.Context,
    box_id: Annotated[str, typer.Argument(help='ID of the box to move')],
    location_key: Annotated[
        str,
        typer.Option(
            help='New location key for the box. Use "None" to move to root '
            'location'
        ),
    ],
):
    """Move a box to a new location."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    is_root_move = location_key.lower() == 'none'
    api_location_key = None if is_root_move else location_key

    box_url = f'{api_endpoint}{ApiPaths.BOXES}{box_id}'
    headers = {API_KEY_NAME: api_key}
    data = {
        'location_key': api_location_key,
    }

    response = requests.patch(box_url, headers=headers, json=data)
    handle_response(response)

    box_data = response.json()

    display_location = 'root location' if is_root_move else location_key

    get_console().print(
        f'Moved box: {box_data["name"]} (ID: {box_data["_id"]}) to location '
        f'{display_location}'
    )


@box_commands.command(name='delete', help='Delete a box by ID')
@require_api_endpoint_and_key()
def delete_box(
    ctx: typer.Context,
    box_id: Annotated[str, typer.Argument(help='ID of the box to delete')],
):
    """Delete a box by its ID."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    box_url = f'{api_endpoint}{ApiPaths.BOXES}{box_id}'
    headers = {API_KEY_NAME: api_key}
    response = requests.delete(box_url, headers=headers)
    if response.status_code == 204:
        get_console().print(f'Successfully deleted box with ID: {box_id}')
    else:
        handle_response(response)


@box_commands.command(name='update', help='Update a box by ID')
@require_api_endpoint_and_key()
def update_box(
    ctx: typer.Context,
    box_id: Annotated[str, typer.Argument(help='ID of the box to update')],
    name: Annotated[
        Optional[str], typer.Option(help='New name for the box')
    ] = None,
    location_key: Annotated[
        Optional[str], typer.Option(help='New location key for the box')
    ] = None,
):
    """Update a box by its ID."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    box_url = f'{api_endpoint}{ApiPaths.BOXES}{box_id}'
    headers = {API_KEY_NAME: api_key}
    data = {
        'name': name,
        'location_key': location_key,
    }

    response = requests.patch(box_url, headers=headers, json=data)
    handle_response(response)

    box_data = response.json()
    get_console().print(
        f'Updated box: {box_data["name"]} (ID: {box_data["_id"]})'
    )


@content_commands.command(name='display', help='Display all content in a box')
@require_api_endpoint_and_key()
def display_box_content(
    ctx: typer.Context,
    box_id: Annotated[
        str, typer.Argument(help='ID of the box to display content')
    ],
):
    """Display all content in a specific box."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    content_url = f'{api_endpoint}{ApiPaths.BOXES}{box_id}/contents'
    headers = {API_KEY_NAME: api_key}

    response = requests.get(content_url, headers=headers)
    handle_response(response)

    console = get_console()
    content_data = response.json()
    if not content_data:
        console.print('No content found in the specified box.')
        raise typer.Exit(code=0)

    table = Table(title=f'Content in Box {box_id}')
    table.add_column('Part Number', justify='left')
    table.add_column('Lot Number', justify='left')
    table.add_column('Part Key', justify='left')
    table.add_column('Count', justify='left')

    # content_data is a list of dictionaries with keys 'item_key' and 'quantity'

    for item in content_data:
        part_number, lot_number = get_part_number_and_lot_from_part_key(
            api_endpoint, api_key, item['item_key']
        )
        table.add_row(
            part_number,
            lot_number,
            item['item_key'],
            str(item['quantity']),
        )

    console.print(table)


def _extract_update_from_content(
    api_endpoint: str, api_key: str, content: List[str]
) -> List[dict]:
    """Extract part_number:lot_number and count from content list."""
    console = get_console()
    try:
        parsed_content = dict(item.split('=', 1) for item in content)
    except ValueError:
        console.print(
            'Content must be in the format part_number:lot_number=count'
        )
        raise typer.Exit(code=1)

    # Convert part_number:lot_number to part_key
    update_data = []
    for part_number_lot_number, count in parsed_content.items():
        try:
            part_number, lot_number = part_number_lot_number.split(':', 1)
        except ValueError:
            console.print(
                f'Invalid format {part_number_lot_number}. Expected '
                'part_number:lot_number.'
            )
            raise typer.Exit(code=1)

        try:
            part_key = get_part_key_from_part_number_and_lot(
                api_endpoint, api_key, part_number, lot_number
            )
        except ValueError:
            console.print(f'Part {part_number}:{lot_number} not found.')
            raise typer.Exit(code=1)

        update_data.append({'item_key': part_key, 'quantity': int(count)})

    return update_data


@content_commands.command(name='set', help='Set the content of a box')
@require_api_endpoint_and_key()
def set_box_content(
    ctx: typer.Context,
    box_id: Annotated[str, typer.Argument(help='ID of the box to set content')],
    content: Annotated[
        List[str],
        typer.Option(
            help='Content to set in the box in the format '
            'part_number:lot_number=count'
        ),
    ],
):
    """Set the content of a specific box."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    update_data = _extract_update_from_content(api_endpoint, api_key, content)

    console = get_console()
    if not update_data:
        console.print('No content provided to set in the box.')
        raise typer.Exit(code=1)

    content_url = f'{api_endpoint}{ApiPaths.BOXES}{box_id}/contents'
    headers = {API_KEY_NAME: api_key}

    response = requests.post(
        content_url, headers=headers, json={'contents': update_data}
    )
    handle_response(response)

    console.print(f'Successfully set content for box ID: {box_id}')


@content_commands.command(name='update', help='Update the content of a box')
@require_api_endpoint_and_key()
def update_box_content(
    ctx: typer.Context,
    box_id: Annotated[
        str, typer.Argument(help='ID of the box to update content')
    ],
    content: Annotated[
        List[str],
        typer.Option(
            help='Content to update in the box in the format '
            'part_number:lot_number=count'
        ),
    ],
):
    """Update the content of a specific box."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    update_data = _extract_update_from_content(api_endpoint, api_key, content)

    console = get_console()
    if not update_data:
        console.print('No content provided to update in the box.')
        raise typer.Exit(code=1)

    content_url = f'{api_endpoint}{ApiPaths.BOXES}{box_id}/contents'
    headers = {API_KEY_NAME: api_key}

    response = requests.patch(
        content_url, headers=headers, json={'contents': update_data}
    )
    handle_response(response)

    table = Table(title=f'Updated content for box {box_id}')
    table.add_column('Part Key', justify='left')
    table.add_column('Count', justify='left')

    for item in response.json():
        table.add_row(
            item['item_key'],
            str(item['quantity']),
        )

    console.print(table)

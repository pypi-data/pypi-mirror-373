"""Command to interact with the locations endpoint."""

from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel, Field
import requests
from rich.table import Table
from rich.tree import Tree
import typer
from typing_extensions import Annotated

from app.console import console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.response_utils import handle_response

logger = logging.getLogger(__name__)

location_commands = typer.Typer()


# Pydanic models for the location and box data for uploading locations as a
# json file.
class Box(BaseModel):
    name: str


class Location(BaseModel):
    name: str
    description: Optional[str] = None
    locations: list[Location] = Field(default_factory=list)
    boxes: list[Box] = Field(default_factory=list)


class LocationList(BaseModel):
    locations: list[Location] = Field(default_factory=list)


def upload_one_location(
    location_url: str,
    box_url: str,
    headers: dict,
    location: Location,
    parent_key: str | None,
) -> str:
    """Upload a single location to the backend."""

    # Upload the location
    result = requests.post(
        location_url,
        headers=headers,
        json={
            'name': location.name,
            'description': location.description,
            'parent_key': parent_key,
        },
    )
    handle_response(result)

    # Get the location ID
    location_id = result.json()['_id']

    # Upload all of the dependent locations
    for child_location in location.locations:
        upload_one_location(
            location_url=location_url,
            box_url=box_url,
            headers=headers,
            location=child_location,
            parent_key=location_id,
        )

    # Upload the boxes
    for box in location.boxes:
        result = requests.post(
            box_url,
            headers=headers,
            json={
                'name': box.name,
                'location_key': location_id,
            },
        )
        handle_response(result)

    return location_id


@location_commands.command(name='display')
@require_api_endpoint_and_key()
def display_locations(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Display all locations in a table format."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    location_url = f'{api_endpoint}{ApiPaths.LOCATIONS}'
    headers = {API_KEY_NAME: api_key}

    page = 1
    size = 50
    locations = []
    while True:
        response = requests.get(
            location_url, headers=headers, params={'page': page, 'size': size}
        )
        handle_response(response)

        data = response.json()
        items = data.get('items', [])
        locations.extend(items)
        if page >= data.get('pages', 1):
            break
        page += 1

    if not locations:
        console.print('No locations found.')
        raise typer.Exit()

    # Display the locations in a table format
    table = Table(title='Locations')
    table.add_column('Name', overflow='fold', min_width=10)
    table.add_column('Description', overflow='fold')
    table.add_column('Key')
    table.add_column('Parent Key')
    if verbose:
        table.add_column('Created At')
        table.add_column('Created By')
        table.add_column('Updated At')
        table.add_column('Updated By')

    for location in locations:
        row_data = [
            location['name'],
            location.get(
                'description',
                '',
            ),
            location.get('_id', ''),
            location.get('parent_key', ''),
        ]
        if verbose:
            row_data.extend(
                [
                    format_utc_to_local(location.get('created_at_utc')),
                    location.get('created_by', ''),
                    format_utc_to_local(location.get('updated_at_utc')),
                    location.get('updated_by', ''),
                ]
            )

        table.add_row(*row_data)

    console.print(table)


@location_commands.command(name='display-tree')
@require_api_endpoint_and_key()
def print_locations_tree(
    ctx: typer.Context,
    show_ids: Annotated[
        bool, typer.Option('--ids', '-i', help='Show location IDs')
    ] = False,
):
    """Display a tree of locations and boxes in a tree like structure."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    location_url = f'{api_endpoint}{ApiPaths.LOCATIONS}'
    box_url = f'{api_endpoint}{ApiPaths.BOXES}'

    def lookup_box(parent_key: str | None, location_tree: Tree):
        """Recursively print the box tree."""
        response = requests.get(
            f'{box_url}',
            headers={'X-API-Key': api_key},
            params={'location_key': parent_key},
        )
        handle_response(response)

        # Work around bug in API returning all boxes when parent key None is
        # specified.
        items = [
            item
            for item in response.json()['items']
            if item['location_key'] == parent_key
        ]
        for box in items:
            location_tree.add(
                f'Box: {box["name"]}'
                + (f' (ID: {box["_id"]})' if show_ids else '')
            )

    def lookup_location(parent_key: Optional[str], tree: Tree):
        """Recursively print the location tree."""
        response = requests.get(
            f'{location_url}',
            headers={API_KEY_NAME: api_key},
            params={'parent_key': parent_key},
        )
        handle_response(response)

        # Work around bug in API returning all locations when parent key None is
        # specified.
        items = [
            item
            for item in response.json()['items']
            if item['parent_key'] == parent_key
        ]

        for location in items:
            location_tree = tree.add(
                location['name']
                + (f' (ID: {location["_id"]})' if show_ids else '')
            )
            lookup_location(location['_id'], location_tree)

        lookup_box(parent_key, tree)

    tree = Tree('root')
    lookup_location(None, tree)
    console.print(tree)


@location_commands.command(name='upload', help='Upload a location json file')
@require_api_endpoint_and_key()
def upload_location(
    locations_file: Annotated[
        str, typer.Argument(help='Path to the locations file (json)')
    ],
    ctx: typer.Context,
):
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    location_url = f'{api_endpoint}{ApiPaths.LOCATIONS}'
    box_url = f'{api_endpoint}{ApiPaths.BOXES}'
    headers = {API_KEY_NAME: api_key}

    with open(locations_file, 'r') as file:
        locations_data = json.load(file)

    locations = LocationList(**locations_data)

    console.log('Uploading locations...')

    for location in locations.locations:
        upload_one_location(
            location_url=location_url,
            box_url=box_url,
            headers=headers,
            location=location,
            parent_key=None,
        )

    console.log('Upload complete.')


@location_commands.command(name='update', help='Update a location')
@require_api_endpoint_and_key()
def update_location(
    ctx: typer.Context,
    location_key: Annotated[str, typer.Argument(help='Location key to update')],
    name: Annotated[
        Optional[str], typer.Option('--name', help='New name for the location.')
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option('--description', help='New description for the location.'),
    ] = None,
    parent_key: Annotated[
        Optional[str],
        typer.Option('--parent-key', help='New parent key for the location.'),
    ] = None,
):
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    location_url = f'{api_endpoint}{ApiPaths.LOCATIONS}'
    headers = {API_KEY_NAME: api_key}

    update = {}
    if name:
        update['name'] = name
    if description:
        update['description'] = description
    if parent_key:
        update['parent_key'] = parent_key

    if not update:
        console.log(
            'No updates provided. Use --name, --description, or --parent-key.'
        )
        raise typer.Exit(code=1)

    response = requests.patch(
        f'{location_url}{location_key}',
        headers=headers,
        json=update,
    )
    handle_response(response)

    console.log('Location updated successfully.')


@location_commands.command(name='create', help='Create a location')
@require_api_endpoint_and_key()
def create_location(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help='Name of the location')],
    description: Annotated[
        Optional[str],
        typer.Option('--description', help='Description of the location.'),
    ] = None,
    parent_key: Annotated[
        Optional[str],
        typer.Option('--parent-key', help='Parent key for the location.'),
    ] = None,
):
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    location_url = f'{api_endpoint}{ApiPaths.LOCATIONS}'
    headers = {API_KEY_NAME: api_key}

    location_data = {
        'name': name,
        'description': description,
        'parent_key': parent_key,
    }

    response = requests.post(
        location_url,
        headers=headers,
        json=location_data,
    )
    handle_response(response)

    console.log('Location created successfully. ID:', response.json()['_id'])


@location_commands.command(name='delete', help='Delete a location')
@require_api_endpoint_and_key()
def delete_location(
    ctx: typer.Context,
    location_key: Annotated[str, typer.Argument(help='Location key to delete')],
    force: Annotated[
        bool,
        typer.Option('--force', help='Force deletion without confirmation.'),
    ] = False,
):
    if not force:
        confirm = typer.confirm(
            'Are you sure you want to delete the location with key: '
            f'{location_key}?'
        )
        if not confirm:
            console.print('Deletion cancelled.')
            raise typer.Exit()

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    location_url = f'{api_endpoint}{ApiPaths.LOCATIONS}'
    headers = {API_KEY_NAME: api_key}

    response = requests.delete(
        f'{location_url}{location_key}',
        headers=headers,
    )
    handle_response(response)

    console.print('Location deleted successfully.')

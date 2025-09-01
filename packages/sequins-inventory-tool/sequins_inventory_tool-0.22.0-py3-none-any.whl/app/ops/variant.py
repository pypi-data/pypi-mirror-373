"""Commands to interact with the variant endpoint."""

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.response_utils import handle_response

variant_commands = typer.Typer()

DEFAULT_PAGE_SIZE = 50


@variant_commands.command(name='display')
@require_api_endpoint_and_key()
def display_variants(
    ctx: typer.Context,
    count: Annotated[
        int,
        typer.Option(
            '--count',
            '-c',
            help='Number of variants to display',
            show_default=True,
        ),
    ] = 50,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Fetch and display all variants in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    url = f'{api_endpoint}{ApiPaths.VARIANTS}'
    headers = {API_KEY_NAME: api_key}

    page = 1
    size = count if count < DEFAULT_PAGE_SIZE else DEFAULT_PAGE_SIZE
    variants = []
    while True:
        response = requests.get(
            url, headers=headers, params={'page': page, 'size': size}
        )
        handle_response(response)

        data = response.json()
        items = data.get('items', [])
        variants.extend(items)
        if len(items) < size:
            break

        if len(variants) >= count:
            break

        page += 1

    if not variants:
        get_console().print('No variants found.')
        raise typer.Exit()

    table = Table(title='Variants')
    table.add_column('chrom', justify='left')
    table.add_column('pos', justify='left')
    table.add_column('id', justify='left')
    table.add_column('ref', justify='left')
    table.add_column('alt', justify='left')
    table.add_column('category', justify='left')
    table.add_column('sv_type', justify='left')
    table.add_column('end', justify='left')
    # Reference variant
    table.add_column('Ref\nchrom', justify='left')
    table.add_column('Ref\npos', justify='left')
    table.add_column('Ref\nid', justify='left')
    table.add_column('Ref\nref', justify='left')
    table.add_column('Ref\nalt', justify='left')
    table.add_column('Ref\ncategory', justify='left')
    table.add_column('Ref\nsv_type', justify='left')
    table.add_column('Ref\nend', justify='left')
    if verbose:
        table.add_column('Created By', justify='left')
        table.add_column('Created At', justify='left')
        table.add_column('Updated By', justify='left')
        table.add_column('Updated At', justify='left')

    for item in variants:
        reference_location = item.get('reference_location') or {}
        row_data = [
            item.get('chrom'),
            str(item.get('pos')),
            item.get('id'),
            item.get('ref'),
            item.get('alt'),
            item.get('category'),
            item.get('svtype', ''),
            item.get('end', ''),
            reference_location.get('chrom', ''),
            str(reference_location.get('pos', '')),
            reference_location.get('id', ''),
            reference_location.get('ref', ''),
            reference_location.get('alt', ''),
            reference_location.get('category', ''),
            reference_location.get('svtype', ''),
            reference_location.get('end', ''),
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

    get_console().print(table)

"""CLI tool for interacting with product numbering in the inventory system."""

import logging
from typing import Any, Optional

import pandas
import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.response_utils import handle_response
from app.utils.string_utils import to_screaming_snake_case

logger = logging.getLogger(__name__)

product_naming_app = typer.Typer()


@product_naming_app.command(name='display')
@require_api_endpoint_and_key()
def display_product_numbering(
    ctx: typer.Context,
    description: Annotated[
        Optional[str], typer.Option(help='Filter by description')
    ] = None,
    category: Annotated[
        Optional[str], typer.Option(help='Filter by category')
    ] = None,
    status: Annotated[
        Optional[str], typer.Option(help='Filter by status')
    ] = None,
    sort_by: Annotated[
        Optional[str], typer.Option(help='Field to sort by')
    ] = None,
    sort_order: Annotated[
        Optional[str], typer.Option(help='Sort order (asc or desc)')
    ] = None,
    size: Annotated[
        int, typer.Option(help='Number of items to return per page')
    ] = 50,
    page: Annotated[int, typer.Option(help='Page number to retrieve')] = 1,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Display all product numbers from the database.

    This command fetches and displays product numbers from the database,
    supporting filtering, sorting, and pagination. It uses a GraphQL query to
    efficiently retrieve the data.

    If no product numbers are found, a message is displayed and the command
    exits.
    """

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    console = get_console()
    graphql_url = f'{api_endpoint}{ApiPaths.GRAPHQL}'
    headers = {API_KEY_NAME: api_key}

    # Use a GraphQL query to fetch part definitions. This allows for more
    # flexible queries and reduces the amount of data transferred.
    query = """
        query GetParts(
            $filters: PartFilterInput,
            $sort: PartSortInput,
            $pagination: PaginationInput
        ) {
            parts(filters: $filters, sort: $sort, pagination: $pagination) {
                items {
                    partNumber
                    name
                    description
                    content
                    category
                    status
                    createdBy
                    createdAtUtc
                    updatedBy
                    updatedAtUtc
                }
            }
        }
    """

    # Prepare variables for the GraphQL query based on the CLI options.
    variables: dict[str, Any] = {
        'filters': {},
        'sort': {},
        'pagination': {'page': page, 'size': size},
    }
    if description:
        variables['filters']['description'] = description
    if category:
        variables['filters']['category'] = category
    if status:
        variables['filters']['status'] = status

    if sort_by:
        variables['sort']['field'] = to_screaming_snake_case(sort_by)
        variables['sort']['direction'] = (sort_order or 'asc').upper()

    # Make the GraphQL request
    result = requests.post(
        graphql_url,
        headers=headers,
        json={'query': query, 'variables': variables},
    )
    handle_response(result)
    data = result.json()
    items = data.get('data', {}).get('parts', {}).get('items', [])

    if not items:
        console.print('No product numbers found.')
        raise typer.Exit()

    table = Table(title='Product Numbers')
    table.add_column('Part Number', justify='left')
    table.add_column('Name')
    table.add_column('Description')
    table.add_column('Content')
    table.add_column('Category')
    table.add_column('Status')
    if verbose:
        table.add_column('Created By', justify='left')
        table.add_column('Created At', justify='left')
        table.add_column('Updated By', justify='left')
        table.add_column('Updated At', justify='left')

    for item in items:
        row_data = [
            item['partNumber'],
            item['name'],
            item['description'],
            item['content'],
            item['category'],
            item['status'],
        ]
        if verbose:
            row_data.extend(
                [
                    item.get('createdBy', ''),
                    format_utc_to_local(item['createdAtUtc']),
                    item.get('updatedBy', ''),
                    format_utc_to_local(item['updatedAtUtc']),
                ]
            )

        table.add_row(*row_data)

    console.print(table)


@product_naming_app.command(name='upload')
@require_api_endpoint_and_key()
def upload_product_numbering_database(
    product_numbering_file: Annotated[
        str, typer.Argument(help='Path to the product numbering file (csv)')
    ],
    ctx: typer.Context,
):
    """Upload a product numbering file to the database.

    This command reads a CSV file containing product numbering information and
    uploads it to the database. It checks for existing part numbers and
    creates new entries if they don't exist.
    """

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    product_naming_url = f'{api_endpoint}{ApiPaths.PART_DEFINITIONS}'

    console = get_console()

    console.log(
        f'Uploading product numbering file: url={product_naming_url}, '
        f'file={product_numbering_file}',
    )

    # Load the file
    data = pandas.read_csv(product_numbering_file).fillna(
        {
            'Content': 'N/A',
            'Category': 'N/A',
            'Part Status': 'pending',
            'Supplier': 'N/A',
            'Cat #': '',
        }
    )

    data.rename(
        columns={'Cat #': 'Cat_Number', 'Part Status': 'status'},
        inplace=True,
    )
    data.columns = data.columns.str.replace(' ', '_').str.lower()

    headers = {API_KEY_NAME: api_key}

    with console.status('Uploading product numbering file...'):
        for _, row in data.iterrows():
            console.log(f'Checking part number {row["part_number"]}')

            result = requests.get(
                f'{product_naming_url}{row["part_number"]}',
                headers=headers,
            )

            if result.status_code == 404:
                # If the part does not have a category, we cannot create it.
                if row['category'] == 'N/A':
                    console.log(
                        f'Part number {row["part_number"]} has no category, '
                        f'skipping.'
                    )
                    continue

                console.log(
                    f'Part number {row["part_number"]} not found, '
                    f'creating new entry.'
                )
                response = requests.post(
                    product_naming_url,
                    headers=headers,
                    json={
                        'part_number': row['part_number'],
                        'name': row['name'],
                        'description': row['description'],
                        'content': row['content'],
                        'category': row['category'],
                        'status': str(row['status']).lower().strip(),
                        'supplier': {
                            'name': row['supplier'],
                            'catalogue': str(row['cat_number']),
                        },
                    },
                )
                handle_response(response)
                console.log(f'Created new part number {row["part_number"]}')
            elif result.status_code == 200:
                console.log(
                    f'Part number {row["part_number"]} already exists, '
                    'skipping.'
                )
                # TODO(slangley): Check if the part needs to be updated.
            else:
                logger.error(
                    'Error checking product number %s: %s',
                    row['part_number'],
                    result.text,
                )
                handle_response(result)


@product_naming_app.command(name='update')
@require_api_endpoint_and_key()
def update_product_numbering(
    product_number: Annotated[
        str, typer.Argument(help='Part number to update')
    ],
    ctx: typer.Context,
    name: Annotated[
        Optional[str], typer.Option(help='New name for the product number')
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option(help='New description for the product number'),
    ] = None,
    content: Annotated[
        Optional[str], typer.Option(help='New content for the product number')
    ] = None,
    category: Annotated[
        Optional[str], typer.Option(help='New category for the product number')
    ] = None,
    status: Annotated[
        Optional[str], typer.Option(help='New status for the product number')
    ] = None,
):
    """Update a product number in the database.

    This command allows updating the name, description, content, category, and
    status of a product number.
    """

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    graphql_url = f'{api_endpoint}{ApiPaths.GRAPHQL}'
    headers = {API_KEY_NAME: api_key}

    console = get_console()

    update_data = {
        k: (v.lower().strip() if k == 'status' else v)
        for k, v in {
            'name': name,
            'description': description,
            'content': content,
            'category': category,
            'status': status,
        }.items()
        if v is not None
    }

    if not update_data:
        console.log('No updates provided, nothing to do.')
        raise typer.Exit()

    mutation = """
        mutation EditPart($input: EditPartInput!) {
            editPart(input: $input) {
                __typename
                ... on EditPartSuccess {
                    part {
                        partNumber
                    }
                }
                ... on PartNotFoundError {
                    partNumber
                }
            }
        }
    """

    variables = {'input': {'partNumber': product_number, **update_data}}

    response = requests.post(
        graphql_url,
        headers=headers,
        json={'query': mutation, 'variables': variables},
    )

    handle_response(response)
    data = response.json()
    if 'errors' in data:
        for error in data['errors']:
            console.print(f"Error: {error['message']}")
        raise typer.Exit(1)

    result = data.get('data', {}).get('editPart')
    if not result:
        console.print(
            '[bold red]Error: Invalid response from server.[/bold red]'
        )
        raise typer.Exit(1)

    if result.get('__typename') == 'PartNotFoundError':
        console.print(f'Error: Part number {product_number} not found.')
        raise typer.Exit(1)

    console.log(f'Updated product number {product_number}')


@product_naming_app.command(name='create')
@require_api_endpoint_and_key()
def create_product_numbering(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help='Name for the product number')],
    description: Annotated[
        str, typer.Option(help='Description for the product number')
    ],
    content: Annotated[
        str, typer.Option(help='Content for the product number')
    ],
    category: Annotated[
        str, typer.Option(help='Category for the product number')
    ],
    product_number: Annotated[
        Optional[str],
        typer.Option(
            help='Part number to create, if not provided will be auto-generated'
        ),
    ] = None,
    status: Annotated[
        str, typer.Option(help='Status for the product number')
    ] = 'pending',
    supplier_name: Annotated[
        str, typer.Option(help='Supplier for the product number')
    ] = 'Internal',
    supplier_catalogue: Annotated[
        Optional[str], typer.Option(help='Supplied catalogue number')
    ] = None,
):
    """Create a new product number in the database.

    This command creates a new product number with the specified details. If a
    product number is not provided, it will be auto-generated by the system.
    """

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    graphql_url = f'{api_endpoint}{ApiPaths.GRAPHQL}'
    headers = {API_KEY_NAME: api_key}

    mutation = """
        mutation AddPart($input: PartInput!) {
            addPart(input: $input) {
                __typename
                ... on AddPartSuccess {
                    part {
                        partNumber
                        name
                        description
                        content
                        category
                        status
                        createdBy
                        createdAtUtc
                        updatedBy
                        updatedAtUtc
                    }
                }
                ... on PartAlreadyExistsError {
                    partNumber
                }
            }
        }
    """

    variables = {
        'input': {
            'partNumber': product_number,
            'name': name,
            'description': description,
            'content': content,
            'category': category,
            'status': status.lower().strip(),
            'supplier': {
                'name': supplier_name,
                'catalogue': supplier_catalogue,
            },
        }
    }

    response = requests.post(
        graphql_url,
        headers=headers,
        json={'query': mutation, 'variables': variables},
    )

    console = get_console()

    handle_response(response)
    data = response.json()
    if 'errors' in data:
        for error in data['errors']:
            console.print(f"Error: {error['message']}")
        raise typer.Exit(1)

    result = data['data']['addPart']

    if result['__typename'] == 'PartAlreadyExistsError':
        console.print(
            f"Error: Part number '{result['partNumber']}' already exists."
        )
        raise typer.Exit(1)

    console.log('Product number created successfully.')
    item = result['part']

    table = Table(title='Created Product Number')
    table.add_column('Part Number', justify='left')
    table.add_column('Name')
    table.add_column('Description')
    table.add_column('Content')
    table.add_column('Category')
    table.add_column('Status')
    table.add_column('Created By', justify='left')
    table.add_column('Created At', justify='left')
    table.add_column('Updated By', justify='left')
    table.add_column('Updated At', justify='left')

    table.add_row(
        item['partNumber'],
        item['name'],
        item['description'],
        item['content'],
        item['category'],
        item['status'],
        item.get('createdBy', ''),
        format_utc_to_local(item['createdAtUtc']),
        item.get('updatedBy', ''),
        format_utc_to_local(item['updatedAtUtc']),
    )
    console.print(table)

"""CLI to interact with Azenta parts and shipment data."""

import logging
import re

import pandas
import requests
import typer
from typing_extensions import Annotated, List

from app.console import console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.response_utils import handle_response

logger = logging.getLogger(__name__)

azenta_app = typer.Typer()


@azenta_app.command(name='upload-stock')
@require_api_endpoint_and_key()
def upload_stock(
    sample_search_csv: Annotated[
        str, typer.Argument(help='Path to the sample search CSV file')
    ],
    ctx: typer.Context,
):
    """Upload a sample search csv of stock data to the database."""
    logger.info(f'Uploading stock data from {sample_search_csv}...')

    columns = {
        'Originating ID - UDF': 'Originating_ID',
        'Sample Status - UDF': 'status',
        'Division - UDF': 'location',
        'Received Date - UDF': 'received_date',
    }
    # Load the file
    data = pandas.read_csv(
        sample_search_csv, usecols=list(columns.keys())
    )  # pyrefly: ignore[no-matching-overload]
    data.rename(columns=columns, inplace=True)
    data.columns = data.columns.str.replace(' ', '_').str.lower()
    logger.debug(f'Columns: {data.columns}')

    # Get a list of all the parts, the lot number and the counts for each.
    # We need to check if parts exist in the database.
    location_part_and_lot_counts = {}
    for row in data.itertuples():
        parts_and_lot = row.originating_id.split()
        part_number = parts_and_lot[0].upper().strip()
        lot_number = parts_and_lot[1].upper().strip()
        if row.location not in location_part_and_lot_counts:
            location_part_and_lot_counts[row.location] = {}
        if part_number not in location_part_and_lot_counts[row.location]:
            location_part_and_lot_counts[row.location][part_number] = {}
        if (
            lot_number
            not in location_part_and_lot_counts[row.location][part_number]
        ):
            location_part_and_lot_counts[row.location][part_number][
                lot_number
            ] = {'count': 0}
        location_part_and_lot_counts[row.location][part_number][lot_number][
            'count'
        ] += 1

    logger.debug(f'Part and lot counts: {location_part_and_lot_counts}')

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    # For each location, check if the box exists in the database.
    for location in location_part_and_lot_counts.keys():
        result = requests.get(
            f'{api_endpoint}{ApiPaths.BOXES}',
            headers={API_KEY_NAME: api_key},
            params={'box_name': location},
        )
        handle_response(result)
        items = result.json()['items']

        if not items:
            console.log(f'Box {location} not found')
            raise typer.Exit(code=1)

        if len(items) > 1:
            console.log(f'Box {location} found more than one box')
            raise typer.Exit(code=1)

        location_part_and_lot_counts[location]['box_id'] = items[0]['_id']

    # For each part and lot, check if the part exists in the database.
    for location, parts in location_part_and_lot_counts.items():
        for part, lots in parts.items():
            # Don't forget we've saved the box_id in the location so we can
            # update the box later.
            if part == 'box_id':
                continue

            for lot_number in lots.keys():
                result = requests.get(
                    f'{api_endpoint}{ApiPaths.PARTS}',
                    headers={API_KEY_NAME: api_key},
                    params={'part_number': part},
                )
                handle_response(result)
                items = result.json()['items']

                if not items:
                    console.log(f'Part {part} not found')
                    raise typer.Exit(code=1)

                part_item = next(
                    (
                        item
                        for item in items
                        if item['lot_number'] == lot_number
                    ),
                    None,
                )

                # Otherwise might be in the lot constituents.
                if not part_item:
                    for item in items:
                        if (
                            'constituent_lot_numbers' in item
                            and lot_number in item['constituent_lot_numbers']
                        ):
                            part_item = item
                            break

                if not part_item:
                    console.log(f'Part {part} with lot {lot_number} not found')
                    raise typer.Exit(code=1)

                location_part_and_lot_counts[location][part][lot_number][
                    '_id'
                ] = part_item['_id']

    # For each location, set the box count with the parts and counts.
    for location, parts in location_part_and_lot_counts.items():
        box_id = parts.pop('box_id')
        contents = []
        for lots in parts.values():
            for count in lots.values():
                contents.append(
                    {
                        'item_key': count['_id'],
                        'quantity': count['count'],
                    }
                )

        # Posting the contents overwrites the existing contents.
        requests.post(
            f'{api_endpoint}{ApiPaths.BOXES}{box_id}/contents',
            headers={API_KEY_NAME: api_key},
            json={'contents': contents},
        )

    console.log(f'Uploaded stock data from {sample_search_csv} to {location}')
    console.log(f'Contents: {contents}')


def load_shipping_data_from_csv(shipment_csv: str):
    """Load shipping data from a CSV file."""
    columns = {
        'Part No.': 'part_number',
        'Lot.': 'lot_number',
        'Work Order No.': 'work_order_number',
    }
    # Load data from the CSV file
    data = pandas.read_csv(
        shipment_csv, usecols=list(columns.keys())
    )  # pyrefly: ignore[no-matching-overload]
    data.rename(columns=columns, inplace=True)
    data.columns = data.columns.str.replace(' ', '_').str.lower()
    logger.debug(f'Columns: {data.columns}')
    return data


def aggregate_shipping_data(data):
    """Aggregate shipping data by quote number and part/lot counts."""
    order_data = {}
    for row in data.itertuples():
        if not hasattr(row, 'work_order_number'):
            logger.warning(
                'Row %s does not have a work_order_number column', row.Index
            )
            continue
        if not isinstance(row.work_order_number, str):
            logger.warning(
                'Row %s has a non-string work_order_number: %s',
                row.Index,
                row.work_order_number,
            )
            continue
        work_order_number = row.work_order_number.strip()
        if not work_order_number:
            logger.warning('Row %s has an empty work_order_number', row.Index)
            continue
        match = re.search(
            r'Shipment for\s+(\S+)', work_order_number, re.IGNORECASE
        )
        if not match:
            logger.warning(
                'Row %s has an invalid work_order_number: %s',
                row.Index,
                work_order_number,
            )
            continue
        quote_number = match.group(1)
        if quote_number not in order_data:
            order_data[quote_number] = {}

        if row.part_number not in order_data[quote_number]:
            order_data[quote_number][row.part_number] = {}

        if row.lot_number not in order_data[quote_number][row.part_number]:
            order_data[quote_number][row.part_number][row.lot_number] = 1
        else:
            order_data[quote_number][row.part_number][row.lot_number] += 1

    return order_data


def map_part_and_lot_to_part_key(api_endpoint: str, api_key: str, order_data):
    """Map part number and lot number to part key."""
    part_number_and_lot_to_part_key = {}
    for order in order_data.values():
        for part_number, lots in order.items():
            for lot_number in lots.keys():
                if (part_number, lot_number) in part_number_and_lot_to_part_key:
                    continue
                # Check if the part exists in the database.
                result = requests.get(
                    f'{api_endpoint}{ApiPaths.PARTS}',
                    headers={API_KEY_NAME: api_key},
                    params={
                        'part_number': part_number,
                        'lot_number': lot_number,
                    },
                )
                handle_response(result)
                items = result.json()['items']

                if not items:
                    console.log(
                        f'Part {part_number} with lot {lot_number} not found'
                    )
                    console.log('Checking if it is a constituent lot number.')
                    # If not found, check if it is a constituent lot number.
                    result = requests.get(
                        f'{api_endpoint}{ApiPaths.PARTS}',
                        headers={API_KEY_NAME: api_key},
                        params={
                            'part_number': part_number,
                            'constituent_lot_numbers': lot_number,
                        },
                    )
                    handle_response(result)
                    items = result.json()['items']

                if not items:
                    console.log(
                        f'Part {part_number} with lot {lot_number} not found '
                        'as a constituent lot number either.'
                    )
                    raise typer.Exit(code=1)

                # We assume the first item is the correct one.
                if len(items) > 1:
                    console.log(
                        f'Part {part_number} with lot {lot_number} found '
                        f'more than one part: {len(items)}'
                    )
                    raise typer.Exit(code=1)

                part_item = items[0]
                part_key = part_item['_id']
                part_number_and_lot_to_part_key[(part_number, lot_number)] = (
                    part_key
                )
    return part_number_and_lot_to_part_key


def create_one_order(
    api_endpoint: str,
    api_key: str,
    quote_id: str,
    ordered_items: List[dict],
    shipped_items: List[dict],
):
    """Create a new order in the inventory system."""
    create_order_payload = {
        'quote_reference': quote_id,
        'status': 'shipped',
        'items': ordered_items,
        'shipped_items': shipped_items,
    }
    response = requests.post(
        f'{api_endpoint}{ApiPaths.ORDERS}',
        headers={API_KEY_NAME: api_key},
        json=create_order_payload,
    )
    handle_response(response)
    console.log(f'Order {quote_id} created successfully.')


def update_one_order(
    api_endpoint: str, api_key: str, order: dict, shipped_items: List[dict]
):
    """Update an existing order in the inventory system."""
    quote_id = order['quote_reference']
    if order['status'] == 'shipped':
        # If the order is already shipped, check if the shipped items
        # are the same as the ones we are trying to ship.
        existing_shipped_items = order.get('shipped_items', [])
        if existing_shipped_items == shipped_items:
            console.log(
                f'Order {quote_id} already shipped with the same items, '
                'no update required.'
            )
            return
        else:
            console.log(
                f'Order {quote_id} already shipped but with different'
                ' items, updating it.'
            )
    # Update the order
    update_order_payload = {
        'quote_reference': order['quote_reference'],
        'status': 'shipped',
        'shipped_items': shipped_items,
    }
    response = requests.patch(
        f'{api_endpoint}{ApiPaths.ORDERS}update',
        headers={API_KEY_NAME: api_key},
        json=update_order_payload,
    )
    handle_response(response)
    console.log(f'Order {quote_id} updated successfully.')


@azenta_app.command(name='upload-shipment')
@require_api_endpoint_and_key()
def upload_shipment(
    shipment_csv: Annotated[
        str, typer.Argument(help='Path to the shipment CSV file')
    ],
    ctx: typer.Context,
):
    """Upload Azenta shipment details to the inventory system.

    This command will read a CSV file containing shipment details from Azenta
    and upload them to the inventory system.

    If the quote number cannot be found, the a new order in shipped state will
    be created.

    If the quote number can be found, then the order will be marked as shipped
    if it is not already marked as shipped in the System.

    If the order is already marked as shipped, and there is no change in what
    was shipped, then no change will be made.
    """

    data = load_shipping_data_from_csv(shipment_csv)

    # As the same quote can be stored over multiple rows, we need to
    # aggregate the data by quote number and part/lot number counts.

    # We need to extract the quote number from the work_order_number columns.
    # It will be in the format `Shipment for QUO-25HANMS-001`, so we can just
    # take the last word in that column.
    order_data = aggregate_shipping_data(data)

    console.log(f'There are {len(order_data)} orders to process.')

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    # Replace all of the Part Number:Lot Number combinations with part_key,
    # and raise an error if the part_key does not exist in the database.
    part_number_and_lot_to_part_key = map_part_and_lot_to_part_key(
        api_endpoint, api_key, order_data
    )

    for quote_id, order in order_data.items():
        console.log(f'Processing order {quote_id}: {order}')
        # For each order, generate a list of parts that were shipped, as this is
        # used by create and update.
        ordered_items = []
        shipped_items = []
        for part_number, lots in order.items():
            part_number_count = 0
            for lot_number, count in lots.items():
                shipped_items.append(
                    {
                        'part_key': part_number_and_lot_to_part_key[
                            (part_number, lot_number)
                        ],
                        'count': count,
                    }
                )
                part_number_count += count

            ordered_items.append(
                {
                    'part_number': part_number,
                    'count': part_number_count,
                }
            )
        # For each order, we need to
        # - check if it exists in the database,
        # - if it does not exist, create it and set the shipment to the values,
        # - if it does exist, update the shipment with the new values.

        # Lookup the order in the inventory system
        result = requests.get(
            f'{api_endpoint}{ApiPaths.ORDERS}',
            headers={API_KEY_NAME: api_key},
            params={'quoteReference': quote_id.upper()},
        )
        handle_response(result)
        items = result.json()['items']

        # If not found, create a new order in shipped status.
        if not items:
            console.log(f'Order {quote_id} not found, creating it.')
            create_one_order(
                api_endpoint, api_key, quote_id, ordered_items, shipped_items
            )
            console.log(f'Order {quote_id} created successfully.')
        else:
            if len(items) > 1:
                console.log(
                    f'Order {quote_id} found more than one order: {len(items)}'
                )
                raise typer.Exit(code=1)

            # If found, update the order with the new shipped items.
            console.log(f'Order {quote_id} found, checking if update required.')

            update_one_order(api_endpoint, api_key, items[0], shipped_items)

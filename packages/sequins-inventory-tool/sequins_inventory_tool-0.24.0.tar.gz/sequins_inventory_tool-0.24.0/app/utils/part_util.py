"""Various utilities for parts."""

from functools import lru_cache

import requests

from app.constants import API_KEY_NAME, API_REQUEST_TIMEOUT_SEC, ApiPaths
from app.utils.response_utils import handle_response


@lru_cache()
def get_part_number_and_lot_from_part_key(
    api_endpoint: str, api_key: str, part_key: str
) -> tuple[str, str]:
    """For a given part_key, get the part number and lot number.

    As this information is constant, we can cache it for performance.

    Showing the part number and lot number is useful for display purposes.
    """
    part_details_url = f'{api_endpoint}{ApiPaths.PARTS}'
    # We need to lookup the part details from the item key
    part_details = requests.get(
        f'{part_details_url}{part_key}',
        headers={API_KEY_NAME: api_key},
        timeout=API_REQUEST_TIMEOUT_SEC,
    )
    handle_response(part_details)
    part = part_details.json()
    return part['part_number'], part['lot_number']


@lru_cache()
def get_part_key_from_part_number_and_lot(
    api_endpoint: str, api_key: str, part_number: str, lot_number: str
) -> str:
    """For a given part number and lot number, get the part key.

    As this information is constant, we can cache it for performance.
    """
    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    response = requests.get(
        parts_url,
        headers={API_KEY_NAME: api_key},
        params={'part_number': part_number, 'lot_number': lot_number},
        timeout=API_REQUEST_TIMEOUT_SEC,
    )
    handle_response(response)
    parts = response.json().get('items', [])
    if not parts:
        raise ValueError(
            f'No part found with part number {part_number} and lot {lot_number}'
        )
    if len(parts) > 1:
        raise ValueError(
            f'Multiple parts found with part number {part_number} and lot '
            f'{lot_number}'
        )
    return parts[0]['_id']

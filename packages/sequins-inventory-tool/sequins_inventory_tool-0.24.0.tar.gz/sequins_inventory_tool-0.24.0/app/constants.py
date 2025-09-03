"""Application specfic constants."""

from enum import StrEnum

BASE_PATH = '/api/v1'


class ApiPaths(StrEnum):
    """Enum for the paths of the API."""

    ACCESS_AUDIT_LOGS = f'{BASE_PATH}/access_audit_logs/'
    BOXES = f'{BASE_PATH}/box/'
    BLENDS = f'{BASE_PATH}/blend/'
    SEQUINS = f'{BASE_PATH}/sequin/'
    VARIANTS = f'{BASE_PATH}/variant/'
    GROUPS = f'{BASE_PATH}/group/'
    GROUP_LISTS = f'{BASE_PATH}/group_list/'
    LOCATIONS = f'{BASE_PATH}/location/'
    PART_DEFINITIONS = f'{BASE_PATH}/part_definition/'
    TILES = f'{BASE_PATH}/tile/'
    POOLS = f'{BASE_PATH}/pool/'
    PARTS = f'{BASE_PATH}/part/'
    ORDERS = f'{BASE_PATH}/order/'
    USERS = f'{BASE_PATH}/user/'
    GRAPHQL = '/graphql/'


# The name of our API key header.
API_KEY_NAME = 'X-API-Key'


# Timeout for API requests in seconds.
API_REQUEST_TIMEOUT_SEC = 30


PACKAGE_NAME = 'sequins-inventory-tool'

PACKAGE_AUTHOR = 'sequins'

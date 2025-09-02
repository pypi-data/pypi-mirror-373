"""CLI to manipulate the database directly."""

import logging

import pymongo
from pymongo import ASCENDING, IndexModel
import typer

from app.console import console
from app.ops.database_user import app as database_user_app

logger = logging.getLogger(__name__)

app = typer.Typer()
app.add_typer(database_user_app, name='user')

BLEND_COLLECTION_NAME = 'blends'
SEQUIN_COLLECTION_NAME = 'sequins'
VARIANT_COLLECTION_NAME = 'variants'
GROUP_COLLECTION_NAME = 'groups'
LOCATION_COLLECTION_NAME = 'locations'
PART_DEFINITIONS_COLLECTION_NAME = 'part_definitions'
PART_COLLECTION_NAME = 'parts'
TILE_COLLECTION_NAME = 'tiles'
POOL_COLLECTION_NAME = 'pools'
USER_COLLECTION_NAME = 'users'


@app.command(name='create-indexes')
def create_indexes(ctx: typer.Context):
    server = ctx.obj['database_server_name']
    database = ctx.obj['database_name']

    logger.debug('server = %s, database = %s', server, database)

    console.log(f'Creating indexes for database {database}.')

    client = pymongo.MongoClient(server)
    db = client[database]

    # Create indexes for the sequin collection.
    # - Sequin ID must be unique
    # - sequence must be unique.
    sequin_id_index = IndexModel([('id', ASCENDING)], unique=True)
    sequin_sequence_index = IndexModel([('sequence', ASCENDING)], unique=True)
    db[SEQUIN_COLLECTION_NAME].create_indexes(
        [
            sequin_id_index,
            sequin_sequence_index,
        ]
    )

    # Create indexes for the variant collection.
    # Variant are duplicate if chromosome, position, reference, and alt match.
    variant_index = IndexModel(
        [
            ('chrom', ASCENDING),
            ('pos', ASCENDING),
            ('ref', ASCENDING),
            ('alt', ASCENDING),
        ],
        unique=True,
    )
    db[VARIANT_COLLECTION_NAME].create_indexes([variant_index])

    # Create indexes for the group collection.
    # - Group ID must be unique
    group_index = IndexModel([('id', ASCENDING)], unique=True)
    group_sequin_index = IndexModel(
        [('sequin_ids_hash', ASCENDING)], unique=True
    )
    db[GROUP_COLLECTION_NAME].create_indexes([group_index, group_sequin_index])

    # Create indexes for the blend collections.
    # - Blend ID must be unique
    blend_index = IndexModel([('id', ASCENDING)], unique=True)
    db[BLEND_COLLECTION_NAME].create_indexes([blend_index])

    # Create indexes for the part definition collection.
    # - Part number must be unique
    part_index = IndexModel([('part_number', ASCENDING)], unique=True)
    db[PART_DEFINITIONS_COLLECTION_NAME].create_indexes([part_index])

    # Create indexes for the parts collection.
    # For filtering:
    part_number_index = IndexModel([('part_number', ASCENDING)])
    part_and_hash_index = IndexModel(
        [
            ('part_number', ASCENDING),
            ('constituent_lot_numbers_hash', ASCENDING),
        ],
        unique=True,
    )
    location_index = IndexModel([('location', ASCENDING)])
    status_index = IndexModel([('status', ASCENDING)])
    status_and_quote_reference = IndexModel(
        [('status', ASCENDING), ('quote_reference', ASCENDING)]
    )
    created_at_utc = IndexModel([('created_at_utc', ASCENDING)])
    db[PART_COLLECTION_NAME].create_indexes(
        [
            part_number_index,
            part_and_hash_index,
            location_index,
            status_index,
            status_and_quote_reference,
            created_at_utc,
        ]
    )

    # Create indexes for the tile collection
    # - Tile ID must be unique
    tile_index = IndexModel([('id', ASCENDING)], unique=True)
    tile_sequence_index = IndexModel([('sequence', ASCENDING)])
    db[TILE_COLLECTION_NAME].create_indexes([tile_index, tile_sequence_index])

    # Create indexes for the pool collection.
    # - Pool ID must be unique
    pool_index = IndexModel([('id', ASCENDING)], unique=True)
    db[POOL_COLLECTION_NAME].create_indexes([pool_index])

    # Create indexes for the user collection.
    user_index = IndexModel([('username', ASCENDING)], unique=True)
    api_key_index = IndexModel([('api_key_hash', ASCENDING)])
    db[USER_COLLECTION_NAME].create_indexes([user_index, api_key_index])

    # Create indexes for the location collection.
    location_name_index = IndexModel([('name', ASCENDING)])
    parent_key_index = IndexModel([('parent_key', ASCENDING)])
    db[LOCATION_COLLECTION_NAME].create_indexes(
        [location_name_index, parent_key_index]
    )

    console.log('Indexes created successfully.')


@app.command(name='drop')
def drop_database(ctx: typer.Context):
    server = ctx.obj['database_server_name']
    database = ctx.obj['database_name']

    logger.debug('server = %s, database = %s', server, database)

    client = pymongo.MongoClient(server)
    client.drop_database(database)

    console.log('Database dropped successfully.')

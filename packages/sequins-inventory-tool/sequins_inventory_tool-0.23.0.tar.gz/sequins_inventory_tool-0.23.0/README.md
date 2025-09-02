# Inventory Tool

This directory contains the **Inventory Tool**, a utility designed to interact
with the Sequins inventory system.

## Commands

### Database

The `database` command interacts directly with the underlying mongodb instance,
and is used to initialize, delete, or add initial data directly to the database.

* `create-idexes` - Creates the indexes used by mongodb for uniqueness and
searching.
* `drop` - Removes the database from the mongodb server.

### Product Numbering

The `product-numbering` command interacts with the part definition API to list
all defined products in the inventory.

### Location

The `location` command interacts with the location API to list location data in
the inventory system.


### Users

The `user` command interacts with the user API to list users in the inventory.

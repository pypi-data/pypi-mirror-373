import json
import sys

import click
import keyring
from keyring.errors import KeyringLocked

from cadence.api.model.storage import get_masked
from cadence.cli.prompts.storage import read_storage_data_from_user
from cadence.utils.config import read_cadence_config, write_cadence_config
from cadence.utils.keyring import generate_intellij_service_name, get_storage


@click.group()
def storage():
    """Manage storage"""
    pass


@storage.command()
def add():
    cadence_config = read_cadence_config()
    if 'storages' not in cadence_config:
        cadence_config['storages'] = []

    name = click.prompt("Storage name", type=str)
    in_config = name in cadence_config['storages']

    try:
        existing_storage = get_storage(name)
    except KeyringLocked:
        click.echo(f"Storage {name} already exists in keyring, but access denied")
        sys.exit(1)

    if existing_storage is not None:
        existing_storage = get_masked(existing_storage)
        click.echo(f"Storage {name} already exists")
        click.echo(existing_storage.model_dump_json(indent=2))

        if not in_config: # fixme
            cadence_config['storages'].append(name)
            write_cadence_config(cadence_config)
        return

    if in_config:
        click.echo(f"Storage {name} exist in config, but no credentials found")

    new_storage = read_storage_data_from_user(name)

    storage_str = new_storage.model_dump_json(by_alias=True)
    keyring.set_password(generate_intellij_service_name(name), "", storage_str)

    cadence_config['storages'].append(name)
    write_cadence_config(cadence_config)

    click.echo(f"Storage {name} added")


@storage.command()
@click.argument("storage_name", type=str)
def get(storage_name: str):
    storage = get_storage(storage_name)
    if storage:
        storage = get_masked(storage)

    click.echo(storage.model_dump_json(indent=2))


@storage.command("list")
def list_storages():
    cadence_config = read_cadence_config()

    if 'storages' not in cadence_config:
        click.echo("No storages added")
        return
    storages = []
    for storage_name in cadence_config['storages']:
        storage = get_storage(storage_name)
        if storage:
            storages.append(get_masked(storage).model_dump())
        else:
            click.echo(click.style(f"Storage {storage_name} exist in config, but no credentials found", fg="red"), err=True)

    click.echo(json.dumps(storages, indent=2))
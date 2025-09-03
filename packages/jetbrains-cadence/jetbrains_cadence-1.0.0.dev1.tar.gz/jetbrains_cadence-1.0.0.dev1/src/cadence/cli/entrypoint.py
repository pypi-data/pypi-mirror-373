import os
from importlib.metadata import version

import click
import keyring
from click import Context

from cadence.api.CadenceHTTPClient import CadenceHTTPClient, DEFAULT_SERVER_URL
from cadence.utils.config import read_cadence_config
from cadence.cli.execution import execution
from cadence.cli.login import login, user
from cadence.cli.storage import storage
from cadence.cli.workspace import workspace


@click.group()
@click.pass_context
@click.option("--server-url", type=str, default=DEFAULT_SERVER_URL, show_default=True, envvar="CADENCE_SERVER_URL")
@click.version_option(version=version("jetbrains-cadence"), prog_name="JetBrains Cadence CLI")
def root(ctx: Context, server_url: str) -> None:
    ctx.ensure_object(dict)

    token = os.environ.get("CADENCE_TOKEN", keyring.get_password("cadence", "__token__"))
    client = CadenceHTTPClient(server_url=server_url, token=token)
    ctx.obj['server_url'] = server_url
    ctx.obj['client'] = client
    cadence_config: dict[str, str] = read_cadence_config() or {}
    ctx.obj['project_id'] = os.environ.get("CADENCE_WORKSPACE") or cadence_config['project_id']

root.add_command(execution)
root.add_command(workspace)
root.add_command(storage)
root.add_command(login)
root.add_command(user)
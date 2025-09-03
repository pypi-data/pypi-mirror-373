import os
import sys

import click
from click import Context

from cadence.api.CadenceHTTPClient import CadenceHTTPClient
from cadence.utils.config import CADENCE_CONFIG_DIR_PATH, read_cadence_config, write_cadence_config


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--workspace", "project_id", type=str, envvar="CADENCE_WORKSPACE", hidden=True)
def workspace(ctx: Context, project_id: str | None) -> None:
    """Manage workspaces"""
    if ctx.invoked_subcommand:
        return

    source = ctx.get_parameter_source('project_id')
    if project_id:
        click.echo(f"Workspace id is set to '{project_id}' (source: {source.name})")

    cadence_config = read_cadence_config()
    if cadence_config and cadence_config.get('project_id'):
        click.echo(f"Workspace id is set to '{cadence_config.get('project_id')}' (source: CONFIG)")
        project_id = cadence_config.get('project_id')

    if not project_id:
        click.echo(f"Workspace id is not set")
        sys.exit(1)

    client: CadenceHTTPClient = ctx.obj['client']

    project = client.get_project(project_id)

    click.echo(f"Name: {project.name}")
    click.echo(f"Credits: {project.license.balance.credits:.2f}")


@workspace.command()
@click.pass_context
@click.argument("project_id", type=str, required=True, metavar='WORKSPACE_ID')
def set(ctx: Context, project_id: str) -> None:
    if os.environ.get("CADENCE_WORKSPACE"):
        click.echo("Warning: environment variable CADENCE_WORKSPACE is set. Values from config file will be ignored.")

    client: CadenceHTTPClient = ctx.obj['client']

    project = client.get_project(project_id)
    if project is None:
        click.echo(f"Error: Invalid argument. Workspace {project_id} doesn't exist.")
        sys.exit(1)

    ### todo
    cadence_config = read_cadence_config()
    cadence_config['project_id'] = project_id
    write_cadence_config(cadence_config, CADENCE_CONFIG_DIR_PATH / 'config.json')
    ###


    click.echo(f"Workspace is set to '{project_id}'")

    click.echo(f"Name: {project.name}")
    click.echo(f"Credits: {project.license.balance.credits:.2f}")


@workspace.command()
@click.pass_context
@click.option("--show-balance", is_flag=True, default=False)
def list(ctx: Context, show_balance: bool) -> None:
    client: CadenceHTTPClient = ctx.obj['client']
    def gen():
        if show_balance:
            yield f"{'Workspace ID':45}\t{'Workspace name':50}\t{'Credits':10}\n"
            projects = client.get_projects().projects
            yield from [f'{pv.id:45}\t{pv.name:50}\t{pv.license.balance.credits:.2f}\n' for pv in projects]
        else:
            yield f"{'Workspace ID':45}\t{'Workspace name':50}\n"

            project_views = client.get_project_views()
            yield from [f'{pv.id:45}\t{pv.displayName:50}\n' for pv in project_views]

    click.echo_via_pager(gen)

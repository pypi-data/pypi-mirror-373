import json
import sys
from pathlib import Path
from typing import Iterable

import click
from click import Context

from cadence.api.CadenceHTTPClient import CadenceHTTPClient, all_executions
from cadence.api.convert import convert_config_to_start_execution_request
from cadence.api.exceptions import CadenceServerException
from cadence.api.model.Execution import Execution, ExecutionList
from cadence.api.model.StorageType import StorageType
from cadence.api.model.TCLogInputStream import TCLogInputStream
from cadence.api.model.common import Input, Output, S3Credentials
from cadence.api.model.connector import S3Connector
from cadence.api.model.logs import LogType
from cadence.api.sync import s3_sync_local_to_remote, s3_sync_remote_to_local
from cadence.api.utils import EXECUTION_DEFAULT_EXCLUDE_KEYS
from cadence.api.model.JetTrainConfig import read_config
from cadence.cli.utils import get_execution_string


@click.group()
def execution() -> None:
    """Manage executions"""
    pass


@execution.command()
@click.option("--preset", type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path), required=True)
@click.pass_context
def start(ctx: Context, preset: Path) -> None:
    """Start an execution"""
    preset = preset.resolve()
    config = read_config(preset)

    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    user = client.get_current_user()

    request = convert_config_to_start_execution_request(project_id, user, client, config, "execution_name",
                                                        preset.name)

    client.validate_execution_request(project_id, request)

    local_sync = request.metadata.localSync
    if local_sync:
        s3_sync_local_to_remote(local_sync.root, local_sync.uri, local_sync.storage,
                                include=local_sync.include,
                                exclude=local_sync.exclude)

    ex = client.start_execution(project_id, request)
    click.echo(ex.id)


@execution.command()
@click.argument("execution-id", type=str, required=True)
@click.pass_context
def stop(ctx: Context, execution_id: str) -> None:
    """Stops an execution"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    ex = client.cancel_execution(project_id, execution_id)
    match ex.status.upper():
        case "CANCELING":
            click.echo(f'Canceling execution {ex.name} #{ex.id}...')
        case "CANCELED" | "FINISHED":
            click.echo(f'Execution {ex.name} #{ex.id} is already ended with status {ex.status.upper()}')
        case _:
            click.secho(f"Something went wrong while cancelling execution {ex.name} #{ex.id}.\nStatus: {ex.status}",
                        fg="red")


@execution.command()
@click.argument("execution-id", type=str, required=True)
@click.pass_context
def status(ctx: Context, execution_id: str) -> None:
    """Print execution status as a string"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    execution_status = client.get_execution_status(project_id, execution_id)

    click.echo(execution_status)


@execution.command()
@click.argument("execution-id", type=str, required=True)
@click.option("--include", type=click.Choice(Execution.model_fields.keys()), multiple=True, default=None,
              help="A set of fields to include in the output.")
@click.pass_context
def info(ctx: Context, execution_id: str, include: list[str] | None) -> None:
    """Print info about execution in JSON format"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    execution = client.get_execution(project_id, execution_id)

    click.echo(json.dumps(execution.model_dump(mode='json', include=set(include) if include else None,
                                               exclude=EXECUTION_DEFAULT_EXCLUDE_KEYS, exclude_none=True), indent=2))


@execution.command()
@click.argument("execution-id", type=str, required=True)
@click.option("--to", "save_to", type=click.Path(file_okay=False, dir_okay=True, path_type=Path), required=True)
@click.option("--inputs", "include_inputs", is_flag=True, default=False)
@click.option("--no-outputs", "include_outputs", is_flag=True, default=True)
@click.pass_context
def download(ctx: Context, execution_id: str, save_to: Path, include_inputs: bool, include_outputs: bool) -> None:
    """Download execution inputs and outputs"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    execution = client.get_execution(project_id, execution_id)
    save_to.mkdir(parents=True, exist_ok=True)

    execution_inputs = execution.inputs
    execution_outputs = execution.outputs
    data_sources: list[Input | Output] = []

    if include_inputs:
        if len(execution_inputs) == 0:
            click.echo("Warning: Execution has no inputs")
        data_sources.extend([i for i in execution_inputs])  # todo

    if include_outputs:
        if execution.status != "FINISHED" and execution.status != "CANCELED":
            click.echo("Error: Can't download outputs. Execution is still running")
            sys.exit(1)

        if len(execution_outputs) == 0:
            click.echo("Warning: Execution has no outputs")
        data_sources.extend([o for o in execution_outputs])  # todo

    if len(data_sources) == 0:
        click.echo("Nothing to download")
        sys.exit(0)

    with click.progressbar(data_sources, length=len(data_sources), show_percent=True, show_pos=True) as pbar:
        for ds in pbar:
            if not isinstance(ds.connector, S3Connector):
                click.echo(
                    f"Error: can't download data from {ds.connector.credentialsId} {ds.connector.uri} as it is not an S3 storage")
                sys.exit(1)

            match ds.connector.storageType:
                case StorageType.DEFAULT:
                    credentials = client.generate_temporary_credentials(project_id).to_s3_credentials()

                case StorageType.CUSTOM:
                    raise NotImplementedError()
                    # click.echo(
                    #     f"You are using a custom storage. Please set up credentials to {ds.connector.credentialsId} {ds.connector.uri} in your environment")
                    # credentials = S3Credentials(
                    #     accessKeyId=os.environ.get("AWS_ACCESS_KEY_ID"),
                    #     secretAccessKey=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                    #     sessionToken=os.environ.get("AWS_SESSION_TOKEN"),
                    # )

                case _:
                    raise NotImplementedError()

            if isinstance(credentials, S3Credentials):
                s3_sync_remote_to_local(ds.connector.uri, str(save_to), credentials)
                pbar.update(1)
            else:
                click.echo("Something went wrong with credentials")
                sys.exit(1)


@execution.command("list")
@click.option("--offset", type=int, default=0, show_default=True)
@click.option("--count", type=int, default=50, show_default=True)
@click.option("--all", is_flag=True, default=False, help="List all executions. Count and offset are ignored")
@click.option("--json/--table", "is_json", is_flag=True, default=False, help="Output format", show_default=True)
@click.pass_context
def list_executions(ctx: Context, offset: int, count: int, all: bool, is_json: bool) -> None:
    """List executions"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']

    executions: Iterable[Execution]
    executions_list: ExecutionList
    if all:
        executions = all_executions(client, project_id=project_id)
        executions_list = client.get_executions_list(project_id=project_id, offset=0, count=0)
        executions_list.count = executions_list.totalCount
    else:
        executions_list = client.get_executions_list(project_id=project_id, offset=offset, count=count)
        executions = executions_list.executions

    if is_json:
        executions_list.executions = list(executions)
        executions_list.count = len(executions_list.executions)
        click.echo(executions_list.model_dump_json(indent=2))
    else:
        def gen():
            yield f"{'Execution ID':<10}\t{'Execution name'[:32]:>32}\t{'Status'}\t{'Created at':>20}\t{'Started at':>20}\t{'Ended at':>20}\tTotal cost\n"
            for e in executions:
                yield get_execution_string(e)
            yield f"Offset: {executions_list.offset} Count: {executions_list.count} Total count: {executions_list.totalCount}"

        click.echo_via_pager(gen)

@execution.command("logs")
@click.argument("execution-id", type=str, required=True)
@click.pass_context
def logs(ctx: Context, execution_id: str) -> None:
    """Print execution logs"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']

    try:
        client.get_execution_status(project_id, execution_id)
    except CadenceServerException as e:
        click.echo(e.message)
        sys.exit(1)

    log_stream = TCLogInputStream(client, project_id, execution_id)

    while True:
        next_log = log_stream.read_next_log()
        if next_log is None:
            break

        match next_log.type:
            case LogType.WARN:
                color = "white"
            case LogType.ERROR:
                color = "red"
            case _:
                color = "yellow"

        click.secho(next_log.text, fg=color)
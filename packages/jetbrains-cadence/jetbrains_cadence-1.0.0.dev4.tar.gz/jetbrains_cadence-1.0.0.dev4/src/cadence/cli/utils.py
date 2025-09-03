import click

from cadence.api.CadenceHTTPClient import CadenceHTTPClient
from cadence.api.model.Execution import Execution
from cadence.utils.config import read_cadence_config, write_cadence_config


def get_execution_string(execution: Execution) -> str:
    total_cost = execution.billingInfo.totalCost.credits if execution.billingInfo else 0.0

    created_at = execution.createdAt.strftime('%Y-%m-%d %H:%M:%S')
    started_at = execution.startedAt.strftime('%Y-%m-%d %H:%M:%S') if execution.startedAt else ""
    ended_at = execution.endedAt.strftime('%Y-%m-%d %H:%M:%S') if execution.endedAt else ""

    match execution.status:
        case "CANCELED":
            status_color = "white"
        case "FINISHED":
            status_color = "green"
        case "FAILED":
            status_color = "red"
        case "CANCELING":
            status_color = "yellow"
        case _:
            status_color = "white"

    status = click.style(execution.status, fg=status_color)
    return f"{execution.id:<10}\t{execution.name[:32]:>32}  {status}\t{created_at:>20}\t{started_at:>20}\t{ended_at:>20}\t{total_cost:.2f}\n"


def try_update_workspace(client: CadenceHTTPClient):
    projects = client.get_project_views()

    if len(projects) == 0:
        click.secho("No available workspaces found", fg="red")
        return

    cadence_config = read_cadence_config() or {}
    current_project_id = cadence_config.get('project_id')

    project = projects[0]
    if current_project_id:
        matches = [p for p in projects if p.id.lower() == current_project_id.lower()]
        assert len(matches) <= 1, "Something went wrong. Multiple projects with the same id found"
        if len(matches) == 1:
            [project] = matches

    cadence_config['project_id'] = project.id
    write_cadence_config(cadence_config)
    click.secho(f"Workspace is set to {project.displayName} [{project.id}]", fg="green")

import click

from cadence.api.model.Execution import Execution


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

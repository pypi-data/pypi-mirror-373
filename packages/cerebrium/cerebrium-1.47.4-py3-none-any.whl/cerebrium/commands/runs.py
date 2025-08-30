import json
from typing import Annotated

import bugsnag
import typer
from rich.console import Console
from rich.table import Table

from cerebrium.api import cerebrium_request
from cerebrium.utils.logging import cerebrium_log
from cerebrium.context import get_current_project

console = Console()
async_cli = typer.Typer(no_args_is_help=True)


@async_cli.command(
    "list",
    help="""
    List all runs for a specific app.

    Usage: cerebrium runs list APP_NAME [--async]
    """,
)
def list_runs(
    app_name: Annotated[
        str,
        typer.Argument(
            ...,
            help="The name of the app for which to list runs.",
        ),
    ],
    async_only: Annotated[
        bool,
        typer.Option(
            "--async",
            is_flag=True,
            help="Only list runs that were executed asynchronously.",
        ),
    ] = False,
):
    """
    List all runs for the specified app in the current project.
    """
    # Retrieve the current project context
    project_id = get_current_project()
    if project_id is None:
        cerebrium_log(
            level="ERROR",
            message="No project found. Please run 'cerebrium project use PROJECT_ID' to set the current project.",
            prefix="",
        )
        raise typer.Exit(1)

    # Construct the app ID and API endpoint URL
    app_id = f"{project_id}-{app_name}"

    # Add asyncOnly to query parameters if --async is specified
    query_params = {}
    if async_only:
        query_params["asyncOnly"] = "true"

    response = cerebrium_request(
        "GET",
        f"v2/projects/{project_id}/apps/{app_id}/runs",
        query_params,
        requires_auth=True,
    )

    # Handle the API response
    if response.status_code == 200:
        runs = response.json().get("items", [])
        if not runs:
            console.print(f"No runs found for app: {app_name}.")
            return

        # Display runs in a formatted table
        table = Table(title=f"Runs for {app_name}")
        table.add_column("Run ID", style="cyan", no_wrap=True)
        table.add_column("Function Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Created At", style="magenta")
        table.add_column("Async", style="blue")

        for run in runs:
            table.add_row(
                run.get("id", "N/A"),
                run.get("functionName", "N/A"),
                run.get("status", "N/A"),
                run.get("createdAt", "N/A"),
                str(run.get("isAsync", "N/A")),
            )

        console.print(table)
    else:
        # Handle non-200 response codes
        try:
            message = response.json().get("message", response.text)
        except json.JSONDecodeError:
            message = response.text
        cerebrium_log(
            level="ERROR",
            message=f"Failed to list runs for app {app_name}.\n{message}",
            prefix="",
        )
        bugsnag.notify(
            Exception("Error listing runs"),
            meta_data={"project_id": project_id, "app_name": app_name},
            severity="error",
        )
        raise typer.Exit(1)

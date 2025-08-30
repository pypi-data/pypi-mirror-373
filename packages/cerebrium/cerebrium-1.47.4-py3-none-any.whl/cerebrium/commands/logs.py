import time
from typing import Annotated, Optional, List, Dict, Tuple, TypedDict
from urllib.parse import urlencode

import bugsnag
import typer
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from cerebrium.api import cerebrium_request
from cerebrium.utils.logging import cerebrium_log, console
from cerebrium.context import get_current_project

logs_cli = typer.Typer(no_args_is_help=True)


class LogEntry(TypedDict):
    appId: str
    projectId: str
    runId: str
    containerId: str
    containerName: str
    logId: str
    lineNumber: int
    logLine: str
    stream: str  # "stdout" or "stderr"
    timestamp: str


class LogsResponse(TypedDict):
    logs: List[LogEntry]
    nextPageToken: Optional[str]
    hasMore: bool


@logs_cli.command(
    "logs",
    help="""
Usage: cerebrium logs APP_NAME

  Fetch and display logs for the specified app, watching until interrupted.

Options:
  -h, --help          Show this message and exit.

Examples:
  # Get logs of a specific app
  cerebrium logs app-name
    """,
)
def watch_app_logs(
    app_name: Annotated[
        str,
        typer.Argument(
            ...,
            help="The app-name you would like to see the logs for",
        ),
    ],
):
    """
    Fetch and display logs for the specified app, watching until interrupted.
    """
    project_id = get_current_project()

    if project_id is None:
        cerebrium_log(
            level="ERROR",
            message="You are not currently in a project. Please login and try again.",
            prefix="",
        )
        raise typer.Exit(1)

    console.print(
        f"[bold green]Watching logs for app '{app_name}'. Press Ctrl+C to stop.[/bold green]"
    )

    last_log_timestamp = None
    app_id = project_id + "-" + app_name

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            task = progress.add_task("Fetching logs...", total=None)

            while True:
                progress.update(task, description="Fetching logs...")

                logs_data, last_log_timestamp = fetch_logs(
                    project_id, app_id, last_log_timestamp=last_log_timestamp
                )

                if logs_data:
                    progress.refresh()
                    display_logs(logs_data.get("logs", []))
                else:
                    # Optionally, print "No new logs." if desired
                    pass

                # Wait for a few seconds before making another request
                progress.update(task, description="Listening for new logs...")
                time.sleep(5)

    except KeyboardInterrupt:
        console.print("\n[red]Stopped watching logs.[/red]")
        raise typer.Exit(0)


def display_logs(logs_data: List[LogEntry]):
    """
    Display logs in a table format.

    Args:
        logs_data (List[LogEntry]): A list of log entries.
    """
    if logs_data:
        table = Table(box=box.SIMPLE)
        table.add_column("Timestamp", style="cyan")
        table.add_column("Message", style="white")

        for log_entry in logs_data:
            timestamp = log_entry.get("timestamp", "")
            log_line = log_entry.get("logLine", "").rstrip()
            table.add_row(timestamp, log_line)

        console.print(table)


def fetch_logs(
    project_id: str,
    app_id: str,
    run_id: Optional[str] = None,
    last_log_timestamp: Optional[str] = None,
) -> Tuple[LogsResponse, Optional[str]]:
    """
    Fetch logs for the specified app or run.

    Args:
        project_id (str): The project ID.
        app_id (str): The application ID.
        run_id (Optional[str]): The run ID for fetching specific logs (if applicable).
        last_log_timestamp (Optional[str]): The timestamp after which to fetch logs.

    Returns:
        Tuple[List[Dict], Optional[str]]: A tuple containing the list of log entries and the latest timestamp.
    """
    # Prepare query parameters
    query_params = {}
    if last_log_timestamp:
        query_params["afterDate"] = last_log_timestamp
    if run_id:
        query_params["runId"] = run_id

    # Build the URL with query parameters
    url = f"v2/projects/{project_id}/apps/{app_id}/logs"
    if query_params:
        url += "?" + urlencode(query_params)

    # Make the GET request without a request body
    logs_response = cerebrium_request("GET", url, requires_auth=True)

    if logs_response is None:
        cerebrium_log(
            level="ERROR",
            message=f"There was an error getting the logs of app {app_id}. Please login and try again.\nIf the problem persists, please contact support.",
            prefix="",
        )
        bugsnag.notify(
            Exception("There was an error getting app logs"),
            meta_data={"appId": app_id, "runId": run_id},
            severity="error",
        )
        raise typer.Exit(1)

    if logs_response.status_code == 204:
        return LogsResponse(logs=[], nextPageToken=None, hasMore=False), last_log_timestamp

    if logs_response.status_code != 200:
        try:
            message = logs_response.json().get("message", None) or logs_response.json()
        except Exception:
            message = logs_response.text
        cerebrium_log(
            level="ERROR",
            message=f"There was an error getting the logs of app {app_id}.\n{message}",
            prefix="",
        )
        bugsnag.notify(
            Exception("There was an error getting app logs"),
            meta_data={"appId": app_id, "runId": run_id},
            severity="error",
        )
        raise typer.Exit(1)

    logs_data = logs_response.json()

    # Update the last_log_timestamp to the latest timestamp
    if logs_data:
        last_log_timestamp = logs_data.get("logs", [])[-1].get("timestamp", last_log_timestamp)

    return logs_data, last_log_timestamp

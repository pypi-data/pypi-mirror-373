from typing import Annotated

import bugsnag
import typer
from rich import box
from rich import print
from rich.panel import Panel
from rich.table import Table

from cerebrium.api import cerebrium_request
from cerebrium.utils.display import colorise_status_for_rich, pretty_timestamp
from cerebrium.utils.logging import cerebrium_log, console
from cerebrium.context import get_current_project

app_cli = typer.Typer(no_args_is_help=True)


@app_cli.command(
    "list",
    help="""
Usage: cerebrium list

  List all apps under your current context.

Options:
  -h, --help          Show this message and exit.

Examples:
  # List all apps
  cerebrium list
    """,
)
def list_apps():
    project_id = get_current_project()
    app_response = cerebrium_request(
        "GET", f"v2/projects/{project_id}/apps", {}, requires_auth=True
    )
    if app_response is None:
        cerebrium_log(
            level="ERROR",
            message="There was an error getting your apps. Please login and try again.\nIf the problem persists, please contact support.",
            prefix="",
        )
        bugsnag.notify(Exception("There was an error getting apps"), severity="error")
        raise typer.Exit(1)
    if app_response.status_code != 200:
        cerebrium_log(app_response.json())
        cerebrium_log(level="ERROR", message="There was an error getting your apps", prefix="")
        bugsnag.notify(Exception("There was an error getting apps"), severity="error")
        return

    apps = app_response.json()

    apps_to_show: list[dict[str, str]] = []
    for a in apps:
        # if isinstance(a, list):
        # convert updated at from 2023-11-13T20:57:12.640Z to human-readable format
        updated_at = pretty_timestamp(a.get("updatedAt", "None"))

        apps_to_show.append(
            {
                "id": f"{a['id']}",
                "status": colorise_status_for_rich(a["status"]),
                "updatedAt": updated_at,
            }
        )

    # sort by updated date
    apps_to_show = sorted(apps_to_show, key=lambda k: k["updatedAt"], reverse=True)

    # Create the table
    table = Table(title="", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Id")
    table.add_column("Status")
    table.add_column("Last Updated", justify="center")

    for entry in apps_to_show:
        table.add_row(
            entry["id"],
            entry["status"],
            entry["updatedAt"],
        )

    details = Panel.fit(
        table,
        title="[bold] Apps ",
        border_style="yellow bold",
        width=140,
    )
    console.print(details)


@app_cli.command(
    "get",
    help="""
Usage: cerebrium get APP_ID

  Get specific details around an app.

Options:
  -h, --help          Show this message and exit.

Examples:
  # Get details of a specific app
  cerebrium get app-id
    """,
)
def get(
    app_id: Annotated[
        str,
        typer.Argument(
            ...,
            help="The app-id you would like to see the details",
        ),
    ],
):
    """
    Get specific details around an app
    """
    project_id = get_current_project()
    app_response = cerebrium_request(
        "GET", f"v2/projects/{project_id}/apps/{app_id}", {}, requires_auth=True
    )

    if app_response is None:
        cerebrium_log(
            level="ERROR",
            message=f"There was an error getting the details of app {app_id}. Please login and try again.\nIf the problem persists, please contact support.",
            prefix="",
        )
        bugsnag.notify(
            Exception(f"There was an error getting app details for {app_id}"),
            meta_data={"appId": app_id},
            severity="warning",
        )
        raise typer.Exit(1)
    if app_response.status_code != 200:
        message = app_response.json().get("message", None) or app_response.json()
        cerebrium_log(
            level="ERROR",
            message=f"There was an error getting the details of app {app_id}.\n{message}",
            prefix="",
        )
        bugsnag.notify(
            Exception(f"There was an error getting app details for {app_id}"),
            meta_data={"appId": app_id},
            severity="warning",
        )
        return

    json_response = app_response.json()

    table = make_detail_table(json_response)
    details = Panel.fit(
        table,
        title=f"[bold] App Details for {app_id} [/bold]",
        border_style="yellow bold",
        width=140,
    )
    print()
    console.print(details)
    print()


@app_cli.command(
    "delete",
    help="""
Usage: cerebrium delete APP_ID

  Delete an app from Cerebrium.

Options:
  -h, --help          Show this message and exit.

Examples:
  # Delete a specific app
  cerebrium delete app-id
    """,
)
def delete(
    app_id: Annotated[str, typer.Argument(..., help="ID of the Cortex app.")],
):
    print(f'Deleting app "{app_id}" from Cerebrium...')

    if not (app_id.startswith("p-") or app_id.startswith("dev-p-")):
        print(
            f"The app_id '{app_id}' should begin with 'p-', run cerebrium app list to get the correct app_id."
        )
        bugsnag.notify(Exception("Invalid app_id on delete"), severity="error")
        raise typer.Exit(1)

    project_id = get_current_project()
    delete_response = cerebrium_request(
        "DELETE", f"v2/projects/{project_id}/apps/{app_id}", {}, requires_auth=True
    )
    if delete_response is None:
        cerebrium_log(
            level="ERROR",
            message=f"There was an error deleting {app_id}. Please login and try again.\nIf the problem persists, please contact support.",
            prefix="",
        )
        bugsnag.notify(
            Exception("There was an error deleting app"),
            meta_data={"appId": app_id},
            severity="error",
        )
        raise typer.Exit(1)
    if delete_response.status_code == 200:
        print("App deleted successfully.")
        raise typer.Exit(0)
    else:
        bugsnag.notify(
            Exception("App deletion failed"), meta_data={"appId": app_id}, severity="error"
        )
        message = delete_response.json().get("message", None) or delete_response.json()
        status_code = delete_response.status_code
        print(f"App deletion failed. Status: {status_code}\n{message}")
        raise typer.Exit(1)


@app_cli.command("scale")
def app_scaling(
    app_id: Annotated[str, typer.Argument(..., help="The id of your app.")],
    cooldown: Annotated[
        int,
        typer.Option(
            ...,
            min=0,
            help=(
                "Update the cooldown period of your app. "
                "This is the number of seconds before your app is scaled down to the min you have set."
            ),
        ),
    ],
    min_replicas: Annotated[
        int,
        typer.Option(
            ...,
            min=0,
            help="Update the minimum number of replicas to keep running for your app.",
        ),
    ],
    max_replicas: Annotated[
        int,
        typer.Option(
            ...,
            min=1,
            help="Update the maximum number of replicas to keep running for your app.",
        ),
    ],
    response_grace_period: Annotated[
        int,
        typer.Option(
            ...,
            min=1,
            help="Update the amount of time your app has to respond to a request or to gracefully terminate on a scale down SIGTERM signal.",
        ),
    ],
):
    """
    Change the cooldown, min and max replicas of your app via the CLI
    """
    print(f"Updating scaling for app '{app_id}'...")

    project_id = get_current_project()

    if not (app_id.startswith("p-") or app_id.startswith("dev-p-")):
        print(
            f"The app_id '{app_id}' should begin with 'p-', run cerebrium app list to get the correct app_id."
        )
        raise typer.Exit(1)

    body = {}
    if cooldown is not None:
        print(f"\tSetting cooldown to {cooldown} seconds...")
        body["cooldownPeriodSeconds"] = cooldown
    if min_replicas is not None:
        print(f"\tSetting minimum replicas to {min_replicas}...")
        body["minReplicaCount"] = min_replicas
    if max_replicas is not None:
        print(f"\tSetting maximum replicas to {max_replicas}...")
        body["maxReplicaCount"] = max_replicas
    if response_grace_period is not None:
        print(f"\tSetting response grace period to {response_grace_period} seconds...")
        body["responseGracePeriodSeconds"] = response_grace_period

    if not body:
        print("Nothing to update...")
        print("Cooldown, minReplicas and maxReplicas are all None")
        raise typer.Exit(0)

    update_response = cerebrium_request(
        "PATCH", f"v2/projects/{project_id}/apps/{app_id}", body, requires_auth=True
    )

    if update_response is None:
        bugsnag.notify(Exception("There was an error scaling"), severity="warning")
        cerebrium_log(
            level="ERROR",
            message=f"There was an error scaling {app_id}. Please login and try again.\nIf the problem persists, please contact support.",
            prefix="",
        )
        raise typer.Exit(1)

    if update_response.status_code == 200:
        print("App scaled successfully.")
        raise typer.Exit(0)
    else:
        bugsnag.notify(
            Exception(f"There was an error scaling app {app_id}"), severity="warning"
        )
        message = update_response.json().get("message", None) or update_response.json()
        cerebrium_log(
            level="ERROR",
            message=f"There was an error scaling {app_id}.\n{message}",
            prefix="",
        )
        raise typer.Exit(1)


def make_detail_table(data: dict[str, str | int | list[str]]):
    def get_value(key: str):
        return str(data.get(key)) if data.get(key) else "Data Unavailable"

    def add_row(
        leader: str,
        key: str = "",
        value: str | None = None,
        ending: str = "",
        optional: bool = False,
    ):
        if value is None:
            if key not in data:
                ending = ""
            if optional:
                if data.get(key):
                    table.add_row(leader, get_value(key) + ending)
            else:
                table.add_row(leader, get_value(key) + ending)
        else:
            table.add_row(leader, str(value))

    # Create the tables
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Parameter", style="")
    table.add_column("Value", style="")
    table.add_row("APP", "", style="bold")
    table.add_row("ID", str(data.get("id")))
    add_row("Created At", "createdAt", pretty_timestamp(get_value("createdAt")))
    if get_value("createdAt") != get_value("updatedAt"):
        add_row("Updated At", "updatedAt", pretty_timestamp(get_value("updatedAt")))
    table.add_row("", "")
    table.add_row("HARDWARE", "", style="bold")
    table.add_row("Compute", get_value("compute"))
    add_row("CPU", "cpu", ending=" cores")
    add_row("Memory", "memory", ending=" GB")
    if get_value("compute") != "CPU" and "hardware" in data:
        add_row("GPU Count", "gpuCount")

    table.add_row("", "")
    table.add_row("SCALING PARAMETERS", "", style="bold")
    add_row("Cooldown Period", key="cooldownPeriodSeconds", ending="s")
    add_row("Minimum Replicas", key="minReplicaCount")
    add_row("Maximum Replicas", key="maxReplicaCount")

    table.add_row("", "")
    table.add_row("STATUS", "", style="bold")
    add_row("Status", "status", value=colorise_status_for_rich(get_value("status")))
    add_row(
        "Last Build Status",
        value=colorise_status_for_rich(get_value("lastBuildStatus")),
    )
    add_row("Last Build ID", value=get_value("latestBuildId"), optional=True)

    pods = data.get("pods", "")
    if isinstance(pods, list):
        pods = "\n".join(pods)
    if data.get("pods"):
        table.add_row("", "")

        table.add_row("[bold]LIVE PODS[/bold]", str(pods) if pods else "Data Unavailable")

    return table

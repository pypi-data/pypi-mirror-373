from typing import Annotated

import bugsnag
import typer
from rich import box
from rich import print
from rich import print as console
from rich.panel import Panel
from rich.table import Table

from cerebrium.api import cerebrium_request
from cerebrium.utils.logging import cerebrium_log
from cerebrium.context import get_current_project, set_config_value, is_valid_project_id

project_cli = typer.Typer(no_args_is_help=True)


@project_cli.command("current")
def current():
    """
    Get the current project you are working in
    """
    print(f"projectId: {get_current_project()}")


@project_cli.command("list")
def list_projects():
    """
    List all your projects
    """
    projects_response = cerebrium_request("GET", "v2/projects", {}, requires_auth=True)
    if projects_response is None:
        cerebrium_log(
            level="ERROR",
            message="There was an error getting your projects. Please try again and if the problem persists contact support.",
            prefix="",
        )
        bugsnag.notify(Exception("There was an error getting projects"), severity="error")
        raise typer.Exit(1)

    if projects_response.status_code != 200:
        cerebrium_log(
            level="ERROR",
            message="There was an error getting your projects",
            prefix="",
        )
        bugsnag.notify(Exception("There was an error getting projects"), severity="error")
        raise typer.Exit(1)

    if projects_response.status_code == 200:
        projects = projects_response.json()

        # Create the table
        table = Table(title="", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("ID")
        table.add_column("Name")

        for project in projects:
            table.add_row(project["id"], project["name"])

        details = Panel.fit(
            table,
            title="[bold] Projects ",
            border_style="yellow bold",
            width=140,
        )
        console(details)

        print("")
        print(
            f"You can set your current project context by running 'cerebrium project set {projects[0]['id']}'"
        )


@project_cli.command("set")
def set_project(
    project_id: Annotated[
        str,
        typer.Argument(
            help="The projectId of the project you would like to work in",
        ),
    ],
):
    """
    Set the project context you are working in.
    """
    # Validate project ID
    if not is_valid_project_id(project_id):
        print("Invalid Project ID. Project ID should start with 'p-' or 'dev-p-'")
        bugsnag.notify(Exception("Invalid Project ID"), severity="warning")
        raise typer.Exit(1)

    # Set the project using context function
    set_config_value("project", project_id)

    print(f"Project context successfully set to : {project_id}")

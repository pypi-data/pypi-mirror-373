import os
from typing import Optional

import bugsnag
from rich import print
from typer import Typer, Option

from cerebrium import __version__ as cerebrium_version
from cerebrium.commands.app import app_cli
from cerebrium.commands.auth import auth_cli
from cerebrium.commands.project import project_cli
from cerebrium.commands.region import region_cli
from cerebrium.commands.runs import async_cli
from cerebrium.commands.files import files_cli
from cerebrium.commands.logs import logs_cli
from cerebrium.commands.run import run_cli
from cerebrium.commands.deploy import deploy
from cerebrium.commands.init import init
from cerebrium.context import cli_context
from cerebrium.utils.bugsnag_setup import init_bugsnag


bugsnag.configure(
    api_key="606044c1e243e11958763fb42cb751c4",
    project_root=os.path.dirname(os.path.abspath(__file__)),
    release_stage=os.getenv("CEREBRIUM_ENV", "prod"),
    app_version=cerebrium_version,
    auto_capture_sessions=True,
)
init_bugsnag()

cli = Typer(no_args_is_help=True)


@cli.callback()
def main(
    service_account_token: Optional[str] = Option(
        None,
        "--service-account-token",
        help="Service account token for authentication. Takes precedence over environment variable and stored session token.",
    ),
    verbose: bool = Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output to show API calls and responses.",
    ),
):
    """Cerebrium CLI for deploying and managing apps."""
    cli_context.service_account_token = service_account_token
    cli_context.verbose = verbose or os.getenv("CEREBRIUM_VERBOSE", "").lower() in [
        "true",
        "1",
        "yes",
    ]


cli.command("deploy")(deploy)
cli.command("init")(init)
# Add sub-cli's to the main cli
cli.add_typer(auth_cli, help="Authentication commands.")
cli.add_typer(run_cli, help="Run a function in a Cerebrium app.")
cli.add_typer(files_cli, help="Manage files in a Cerebrium app.")
cli.add_typer(logs_cli, help="Fetch and display logs for a Cerebrium app.")
cli.add_typer(
    app_cli,
    name="app",
    help="Manage apps. See a list of apps, app details and scale apps. Run `cerebrium app --help` for more information.",
)
cli.add_typer(
    project_cli,
    name="project",
    help="Manage projects. Run `cerebrium project --help` for more information.",
)
cli.add_typer(
    async_cli,
    name="runs",
    help="Manage runs for a specific app. Run `cerebrium runs --help` for more information.",
)
cli.add_typer(
    region_cli,
    name="region",
    help="Manage default region. Run `cerebrium region --help` for more information.",
)


@cli.command()
def version():
    """
    Print the version of the Cerebrium CLI
    """
    print(cerebrium_version)


if __name__ == "__main__":
    cli()

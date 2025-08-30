import cProfile
import sys
from pstats import Stats
from typing import Annotated, Optional

import bugsnag
import typer
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from cerebrium import __version__
from cerebrium.api import cerebrium_request
from cerebrium.config import (
    get_validated_config,
)
from cerebrium.context import get_current_project, cli_context
from cerebrium.utils.check_cli_version import print_update_cli_message
from cerebrium.utils.deploy import package_app, get_function_names
from cerebrium.utils.display import confirm_partner_service_deployment
from cerebrium.utils.logging import cerebrium_log, console

cortex_cli = typer.Typer(no_args_is_help=True)


def print_user_messages():
    from cerebrium.api import fetch_notifications

    notifications = fetch_notifications()

    if notifications:
        console.print("\n[yellow]ℹ️  Important Notice:[/yellow]")
        for message in notifications:
            console.print(message["message"])
            if "link" in message and "linkText" in message:
                console.print(f"{message['linkText']} ({message['link']})")


@cortex_cli.command("deploy")
def deploy(
    name: Annotated[
        Optional[str],
        typer.Option(
            "--name",
            help="Name of the App. Overrides the value in the TOML file if provided.",
        ),
    ] = None,
    disable_syntax_check: Annotated[
        bool, typer.Option(help="Flag to disable syntax check.")
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(
            help="Log level for the Cortex deployment. Can be one of 'DEBUG' or 'INFO'",
        ),
    ] = "INFO",
    config_file: Annotated[
        str,
        typer.Option(
            help="Path to the cerebrium config TOML file. You can generate a config using `cerebrium init`."
        ),
    ] = "./cerebrium.toml",
    disable_confirmation: Annotated[
        bool,
        typer.Option(
            "--disable-confirmation",
            "-y",
            help="Disable the confirmation prompt before deploying.",
        ),
    ] = False,
    disable_animation: Annotated[
        bool,
        typer.Option(
            "--disable-animation",
            help="Disable TQDM loading bars and yaspin animations.",
        ),
    ] = False,
    disable_build_logs: Annotated[
        bool,
        typer.Option("--disable-build-logs", help="Disable build logs during a deployment."),
    ] = False,
):
    """
    Deploy a new Cortex app to Cerebrium. Run `cerebrium deploy --help` for more information.\n
        \n
    Usage: cerebrium deploy [OPTIONS]\n
    \n
      Deploy a Cortex app to Cerebrium.\n
    \n
    Options:\n
      --name TEXT                    Name of the App. Overrides the value in the TOML file if provided.\n
      --disable-syntax-check         Flag to disable syntax check.\n
      --log-level [DEBUG|INFO]       Log level for the Cortex deployment. Can be one of 'DEBUG' or 'INFO'.\n
      --config-file PATH             Path to the cerebrium config TOML file. You can generate a config using `cerebrium init`.\n
      -y, --disable-confirmation     Disable the confirmation prompt before deploying.\n
      --disable-animation            Disable TQDM loading bars and yaspin animations.\n
      --disable-build-logs           Disable build logs during a deployment.\n
      -h, --help                     Show this message and exit.\n
    \n
    Examples:\n
      # Deploy an app with the default settings\n
      cerebrium deploy\n
    \n
      # Deploy an app with a custom name and disabled syntax check\n
      cerebrium deploy --name my_app --disable-syntax-check\n
    """
    print_update_cli_message()

    log_level = log_level.upper()
    assert log_level in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "INTERNAL",
    ], "Log level must be one of 'DEBUG' or 'INFO'"

    with cProfile.Profile() as pr:
        project_id = get_current_project()
        config = get_validated_config(config_file, name, False)

        if config.partner_services is not None:
            payload = config.to_payload()
            if not disable_confirmation and not confirm_partner_service_deployment(config):
                sys.exit()

            console.print("Deploying partner service app...")
            payload["cliVersion"] = __version__
            setup_response = cerebrium_request(
                "POST",
                f"v2/projects/{project_id}/partner-apps",
                payload,
                requires_auth=True,
            )

            if setup_response is None or setup_response.status_code != 200:
                error_message = "Error deploying partner app. Please check the dashboard or contact support if the issue persists."
                try:
                    if setup_response is not None:
                        response_json = setup_response.json()
                        if isinstance(response_json, dict) and isinstance(
                            response_json.get("message"), str
                        ):
                            error_message = response_json["message"]
                except Exception:
                    pass

                console.print(Text(error_message, style="red"))
                bugsnag.notify(Exception(error_message), severity="error")
                raise typer.Exit(1)

            dashboard_url = setup_response.json()["dashboardUrl"]
            app_endpoint = setup_response.json()["internalEndpoint"]
            info_string = f"App Dashboard: {dashboard_url}\n\nEndpoint:\n[bold red]POST[/bold red] {app_endpoint}"
            dashboard_info = Panel(
                info_string,
                title=f"[bold green] {config.deployment.name} is now live!  ",
                border_style="green",
                width=140,
            )
            console.print(Group(dashboard_info))
            print_user_messages()
            return typer.Exit(0)

        build_status, setup_response = package_app(
            config,
            disable_build_logs,
            log_level,  # type: ignore
            disable_syntax_check,
            disable_animation,
            disable_confirmation,
        )
        if setup_response is None:
            message = "Error building app. Please check the dashboard or contact support if the issue persists."
            cerebrium_log(message=message, color="red")
            bugsnag.notify(Exception(message), severity="warning")
            raise typer.Exit(1)
        if build_status in ["success", "ready"]:
            endpoint = setup_response["internalEndpoint"]
            dashboard_url = setup_response["dashboardUrl"]
            info_string = f"App Dashboard: {dashboard_url}\n\nEndpoints:"
            function_names = get_function_names(config.custom_runtime is not None)
            for method, function_name in function_names:
                info_string += f"\n[bold red]{method}[/bold red] {endpoint}/" + function_name

            dashboard_info = Panel(
                info_string,
                title=f"[bold green] {config.deployment.name} is now live!  ",
                border_style="green",
                width=140,
            )
            console.print(Group(dashboard_info))
            print_user_messages()
        elif build_status in ["build_failure", "init_failure", "init_timeout", "cancelled"]:
            if cli_context.verbose:
                cerebrium_log(f"Build failed with status: {build_status}", color="yellow")
                cerebrium_log(f"App name: {config.deployment.name}", color="yellow")
                cerebrium_log(f"Project ID: {project_id}", color="yellow")
                if setup_response:
                    cerebrium_log(f"Setup response: {setup_response}", color="yellow")

            if build_status == "cancelled":
                console.print(Text("Build was cancelled", style="yellow"))
            else:
                error_details = {
                    "build_status": build_status,
                    "app_name": config.deployment.name,
                    "project_id": project_id,
                    "log_level": log_level,
                    "config_file": config_file,
                    "cli_version": __version__,
                }
                if setup_response:
                    error_details["setup_response"] = setup_response

                bugsnag.notify(
                    Exception(f"User build failed with status: {build_status}"),
                    severity="warning",
                    metadata={"build_details": error_details},
                )
                console.print(
                    Text("Unfortunately there was an issue with your build", style="red")
                )
            raise typer.Exit(1)
    pr.disable()
    if log_level == "INTERNAL":
        Stats(pr).sort_stats("tottime").print_stats(10)

from json.decoder import JSONDecodeError

import typer
from requests.exceptions import RequestException

from cerebrium import api
from cerebrium.utils.logging import cerebrium_log
from cerebrium.context import get_current_project


def _graceful_shutdown(
    app_name: str,
    build_id: str,
    is_interrupt: bool = False,
):
    """
    This function is called when the user presses Ctrl+C while streaming logs.
    - stops the spinner
    - sends a kill signal to the backend to stop the build job
    - prints a message
    - exits the program
    """
    if is_interrupt:
        cerebrium_log("\n\nCtrl+C detected. Shutting down current build...", color="yellow")

    try:
        project_id = get_current_project()
        if project_id is None:
            cerebrium_log(
                message="No project context found. Please login and try again.",
                level="ERROR",
            )
            raise typer.Exit(1)

        app_id = project_id + "-" + app_name

        response = api.cerebrium_request(
            http_method="DELETE",
            url=f"v2/projects/{project_id}/apps/{app_id}/builds/{build_id}",
            payload={},
            requires_auth=True,
        )
        if response is None:
            cerebrium_log(
                message="Error ending build. Please check your internet connection and try again.\nIf the problem persists, please contact support.",
                level="ERROR",
            )
            raise typer.Exit(1)
        if response.status_code != 200:
            try:
                json_response = response.json()
                if "message" in json_response:
                    cerebrium_log(
                        f"Error ending session: {response.json()['message']}",
                        level="ERROR",
                    )
                raise typer.Exit(1)
            except JSONDecodeError:
                cerebrium_log(
                    f"Error ending session{':' + response.text if response.text else ''}",
                    level="ERROR",
                )
                raise typer.Exit(1)

        raise typer.Exit(0)

    except RequestException as e:
        cerebrium_log(f"Error ending session: {e}", level="ERROR")
        raise typer.Exit(1)

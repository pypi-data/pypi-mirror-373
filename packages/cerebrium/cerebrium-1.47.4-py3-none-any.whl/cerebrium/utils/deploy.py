import os
import re
import sys
import time
from datetime import datetime
from typing import Any

import bugsnag
import pytz
import typer
from rich import print
from rich.live import Live
from rich.spinner import Spinner
from tzlocal import get_localzone

from cerebrium import __version__, api
from cerebrium.api import (
    cerebrium_request,
    upload_cortex_files,
)
from cerebrium.config import CerebriumConfig
from cerebrium.context import get_current_project
from cerebrium.types import LogLevel
from cerebrium.utils.display import confirm_deployment
from cerebrium.utils.files import determine_includes
from cerebrium.utils.logging import cerebrium_log, console
from cerebrium.utils.termination import _graceful_shutdown
from cerebrium.utils.verification import run_pyflakes

CEREBRIUM_ENV = os.getenv("CEREBRIUM_ENV", "prod")

# Default FastAPI entrypoint for uvicorn
DEFAULT_ENTRYPOINT = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


def _create_new_app_request(
    payload: dict,
) -> dict[str, Any]:
    project_id = get_current_project()
    setup_response = cerebrium_request("POST", f"v2/projects/{project_id}/apps", payload)
    status_code = setup_response.status_code
    if setup_response is None:
        cerebrium_log(
            level="ERROR",
            message=f"An unknown error occurred when deploying your app. Please login and try again. If the error "
            f"continues to persist, contact support. Status code: {status_code}",
            prefix="",
        )
        bugsnag.notify(
            Exception("Error deploying app, no response from create app"), severity="error"
        )
        raise typer.Exit(1)

    if setup_response.status_code == 401 or setup_response.status_code == 403:
        cerebrium_log(
            level="ERROR",
            message="You must log in to use this functionality. Please run 'cerebrium login'",
            prefix="",
        )
        bugsnag.notify(
            Exception(
                f"User not logged in on deploy command. {status_code} response from create app"
            ),
            severity="warning",
        )
        raise typer.Exit(1)

    if setup_response.status_code != 200:
        # Safely get the error message from the response
        error_message = setup_response.json().get("message", "Unknown error")

        cerebrium_log(
            message=f"There was an error deploying your app. Status: {status_code}\n{error_message}",
            prefix="",
            level="ERROR",
        )
        bugsnag.notify(
            Exception(
                f"Error deploying app, non-200 response from create app. Project ID {project_id}. Status: {status_code} Error: {error_message}"
            ),
            severity="warning",
        )
        raise typer.Exit(1)
    return setup_response.json()


def package_app(
    config: CerebriumConfig,
    disable_build_logs: bool,
    log_level: LogLevel,
    disable_syntax_check: bool,
    disable_animation: bool,
    disable_confirmation: bool,
) -> tuple[str, dict[str, Any]]:
    # Get the files in the users directory
    file_list = determine_includes(
        include=config.deployment.include,
        exclude=config.deployment.exclude,
    )
    if file_list == []:
        cerebrium_log(
            "No files to upload. Please ensure you have files in your project.",
            level="ERROR",
        )
        raise typer.Exit(1)

    # Check if user has a Dockerfile or custom entrypoint
    has_dockerfile = (
        config.custom_runtime is not None and config.custom_runtime.dockerfile_path != ""
    )
    has_custom_entrypoint = (
        config.custom_runtime is not None
        and config.custom_runtime.entrypoint != DEFAULT_ENTRYPOINT
    )

    # Only require main.py if user doesn't have a Dockerfile AND doesn't have a custom entrypoint
    if (
        not has_dockerfile
        and not has_custom_entrypoint
        and "./main.py" not in file_list
        and "main.py" not in file_list
    ):
        cerebrium_log(
            "main.py not found. Please ensure your project has a main.py file.",
            level="ERROR",
        )
        raise typer.Exit(1)

    dockerfile_path = (
        config.custom_runtime.dockerfile_path
        if config.custom_runtime is not None
        else "./Dockerfile"
    )
    if (
        config.custom_runtime is not None
        and config.custom_runtime.dockerfile_path != ""
        and not os.path.isfile(dockerfile_path)
    ):
        cerebrium_log(
            "Dockerfile not found. Please ensure your project has a Dockerfile.",
            level="ERROR",
        )

    if not disable_syntax_check:
        try:
            errors, warnings = run_pyflakes(files=file_list, print_warnings=True)
            if errors or warnings:
                proceed_with_error = typer.confirm(
                    "Your deployment has linting errors. Do you want to ignore this and proceed with deployment?",
                    default=True,
                    show_default=True,
                    abort=True,
                )
                if not proceed_with_error:
                    sys.exit(1)
        #             handle typer no confirm
        except typer.Abort as e:
            sys.exit(1)
        except Exception as e:
            bugsnag.notify(e, severity="warning")
            cerebrium_log(
                f"Error occurred during linting. Consider running PyFlakes manually to debug. Or use the `--disable-syntax-check` flag to disable the check on deployment.",
                level="ERROR",
            )
            sys.exit(1)

    if not disable_confirmation:
        if not confirm_deployment(config):
            sys.exit()

    payload = config.to_payload()
    payload["logLevel"] = log_level
    payload["disableBuildLogs"] = disable_build_logs
    payload["cliVersion"] = __version__

    setup_response = _create_new_app_request(payload)

    build_id = setup_response["buildId"]
    print(f"Build ID: {build_id}")
    build_status = str(setup_response["status"])

    if build_status == "pending":
        upload_cortex_files(
            build_id=build_id,
            cerebrium_config=config,
            upload_url=setup_response["uploadUrl"],
            zip_file_name=os.path.basename(setup_response["keyName"]),
            config=config,
            file_list=file_list,
            disable_animation=disable_animation,
        )

    build_status = poll_build_logs(
        build_id=build_id,
        deployment_name=config.deployment.name,
        build_status=build_status,
        disable_animation=disable_animation,
    )

    return build_status, setup_response


def format_created_at(created_at: str) -> str:
    """
    Formats the created_at timestamp to a nice local time format.

    Args:
        created_at (str): The original timestamp.

    Returns:
        str: The formatted local time string.
    """
    # Handle different timestamp formats
    try:
        # First try with fractional seconds
        if "." in created_at:
            # Split the timestamp at the decimal point
            date_part, fraction_part = created_at.split(".")
            # Remove the 'Z' and truncate to 6 digits if longer
            fraction_part = fraction_part.rstrip("Z")[:6]
            # Reconstruct with exactly 6 digits
            created_at_normalized = f"{date_part}.{fraction_part}Z"
            utc_time = datetime.strptime(created_at_normalized, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            # Try without fractional seconds
            created_at_normalized = created_at.rstrip("Z")
            utc_time = datetime.strptime(created_at_normalized, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # If all else fails, return the original timestamp
        return created_at

    local_tz = get_localzone()
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_time.strftime("%H:%M:%S")


idle_intervals = [20, 60, 120, 180]
idle_messages = [
    "Hang in there, still building!",
    "Still building, thanks for your patience!",
    "Almost there, please hold on!",
    "Thank you for waiting, we're nearly done!",
]


def poll_build_logs(
    build_id: str,
    deployment_name: str,
    build_status: str,
    disable_animation: bool = False,
    interval: int = 2,
    build_type: str = "App",
) -> str:
    """
    Polls logs at specified intervals and prints only new log lines. Handles the polling of logs with optional spinner and status handling.

    Args:
        build_id (str): The unique identifier of the build.
        deployment_name (str): The name of the deployment.
        build_status (str): The current build status.
        disable_animation (bool): Flag to disable the spinner animation.
        interval (int): The interval in seconds between polls. Defaults to 2 seconds.
        build_type (str): The type of build.

    Returns:
        str: The final build status.
    """
    seen_logs: set[tuple[str, str]] = set()
    spinner = None
    last_log_time = datetime.now()
    next_idle_update_index = 0

    if build_status == "pending" or build_status == "building":
        spinner = (
            None
            if disable_animation
            else Spinner("dots", f"Building {build_type}...", style="gray")
        )

        live = Live(spinner, console=console, refresh_per_second=10)
        live.start()
        try:
            while build_status not in [
                "success",
                "build_failure",
                "init_failure",
                "ready",
                "failure",
                "cancelled",
                "init_timeout",
            ]:
                logs_response = api.fetch_build_logs(deployment_name, build_id)
                build_status = logs_response["status"]
                current_log_lines = logs_response["logs"]

                for log_entry in current_log_lines:
                    created_at = format_created_at(log_entry.get("createdAt"))
                    log_text = log_entry.get("log")
                    log_key = (created_at, log_text)  # Create a hashable key

                    if log_key not in seen_logs:
                        # Handle both \r\n and \n line endings
                        log_text = log_text.replace("\r\n", "\n").replace("\r", "\n")

                        # Split the log text by newlines and print each line with timestamp
                        log_lines = log_text.split("\n")

                        for line in log_lines:
                            if line.strip():  # Only print non-empty lines
                                formatted_line = f"{created_at} {line}"
                                if "error" in line.lower():
                                    cerebrium_log(formatted_line, level="ERROR")
                                else:
                                    cerebrium_log(formatted_line)
                        seen_logs.add(log_key)
                        last_log_time = datetime.now()
                        next_idle_update_index = 0
                        if spinner:
                            spinner.text = f"Building {build_type}..."

                # Check idle time and update spinner message if necessary
                idle_time = (datetime.now() - last_log_time).total_seconds()
                if (
                    spinner
                    and next_idle_update_index < len(idle_intervals)
                    and idle_time >= idle_intervals[next_idle_update_index]
                ):
                    spinner.text = (
                        idle_messages[next_idle_update_index % len(idle_messages)]
                        or f"Building {build_type}..."
                    )
                    next_idle_update_index += 1

                time.sleep(interval)
        except KeyboardInterrupt:
            live.stop()
            _graceful_shutdown(
                app_name=deployment_name,
                build_id=build_id,
                is_interrupt=True,
            )
        finally:
            live.stop()
    else:
        if spinner:
            spinner.stop(text="Build failed")
        cerebrium_log("ERROR", "Build failed.")

    return build_status


def get_function_names(asgi: bool) -> list[tuple[str, str]]:
    """
    Extracts function names and methods from a Python file.
    - If `asgi` is True, looks for FastAPI-style decorators and extracts the method and the function name.
    - If `asgi` is False, extracts function names and assigns a default method ('POST').

    Returns:
        List of tuples (method, function_name).
    """
    try:
        # Check if main.py exists before trying to read it
        if not os.path.exists("main.py"):
            # If main.py doesn't exist, return default placeholder
            return [("POST", "{function_name}")]

        # Read the content of the main.py file
        with open("main.py", "r") as file:
            python_file_content = file.read()

        if asgi:
            # Regular expression to match FastAPI route decorators and the following function name
            asgi_pattern = r"@app\.(get|post|put|delete|patch|options|head)\(['\"].*?['\"]\)\s*\ndef\s+([a-zA-Z_]\w*)\s*\(.*?\):"
            matches = re.findall(asgi_pattern, python_file_content)
            # Returns a list of tuples (method, function_name)
            function_names = [(method.upper(), func_name) for method, func_name in matches]
        else:
            # Regular expression to match 'def' and 'async def' function definitions
            function_pattern = r"(?:async\s+)?def\s+([a-zA-Z_]\w*)\s*\(.*?\):"
            matches = re.findall(function_pattern, python_file_content)
            # Assign default method 'POST' for non-ASGI
            function_names = [("POST", func_name) for func_name in matches]

        # Return the list of function names or a default placeholder if empty
        return function_names if function_names else [("POST", "{function_name}")]

    except Exception as e:
        print(f"Error occurred: {e}")
        return [("POST", "{function_name}")]

import json
import os
import tarfile
import tempfile
import time
from io import StringIO
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.live import Live
from rich.spinner import Spinner

from cerebrium import api
from cerebrium.api import cerebrium_request
from cerebrium.config import get_validated_config
from cerebrium.image import create_base_image
from cerebrium.utils.deploy import format_created_at
from cerebrium.utils.files import determine_includes
from cerebrium.context import get_current_project, get_default_region

run_cli = typer.Typer(no_args_is_help=True)


@run_cli.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    ctx: typer.Context,
    filename: str = typer.Argument(..., help="Name of the entry file"),
    data: str = typer.Option(None, "--data", help="JSON data to pass to the app"),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="Region for the app execution"
    ),
):
    """
    Run a given file in the current project context. Run `cerebrium run --help` for more information.

    This command packages the current directory into a tar file and uploads it to Cerebrium.\n
    Cerebrium will then execute the specified entry file.\n
    If a `cerebrium.toml` file is present, it will be used to configure the app.\n
    If no app name is provided, the current directory name will be used as the app name.\n
    If dependencies are specified in the `cerebrium.toml` file, a base image will be created and used for the run.\n
    If a base image with the same dependencies already exists, it will be reused.\n
    If no dependencies are specified, the default base image will be used.
    """
    project_id = get_current_project()
    if not project_id:
        print("[red]❌ Could not find a project context.[/red]")
        raise typer.Exit(1)

    if data and ctx.args:
        print("[red]❌ Cannot pass both --data and individual data arguments.[/red]")
        raise typer.Exit(1)

    if ctx.args and not data:
        data_dict = {}
        i = 0
        while i < len(ctx.args):
            arg = ctx.args[i]

            if not arg.startswith("--"):
                print(
                    f"[red]❌ '{arg}' is an invalid argument. Use '--{{argument_name}}={{value}}' or '--{{argument_name}} {{value}}'[/red]"
                )
                raise typer.Exit(1)

            arg = arg[2:]  # remove leading --

            if "=" in arg:
                key, value = arg.split("=", maxsplit=1)
            else:
                if i + 1 >= len(ctx.args):
                    print(f"[red]❌ Missing value for argument '--{arg}'[/red]")
                    raise typer.Exit(1)
                if ctx.args[i + 1].startswith("--"):
                    print(
                        f"[red]❌ '{ctx.args[i + 1]}' is an invalid value. Split arguments cannot begin with '--'[/red]"
                    )
                    raise typer.Exit(1)
                key = arg
                i += 1
                value = ctx.args[i]

            data_dict[key] = value
            i += 1
        data = json.dumps(data_dict)

    # input filename::function_name, split it by '::'
    function_name = None
    if "::" in filename:
        parts = filename.split("::")
        if len(parts) != 2:
            print("[red]❌ Invalid filename format. Use 'filename::function_name'[/red]")
            raise typer.Exit(1)
        filename, function_name = parts

    if not filename:
        print("[red]❌ No filename provided. Please specify the entry file name.[/red]")
        raise typer.Exit(1)

    if not filename.endswith(".py"):
        print(f"[red]❌ Invalid file type. Expected a Python file (.py), got: {filename}[/red]")
        raise typer.Exit(1)

    # Check if the Python file exists
    if not Path(filename).exists():
        print(f"[red]❌ File not found: {filename}[/red]")
        raise typer.Exit(1)

    # Check if we need to inject main guard (only if no function is specified)
    needs_main_injection = False
    if "::" not in filename:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                if 'if __name__ == "__main__":' not in content:
                    needs_main_injection = True
        except Exception as e:
            print(f"[red]❌ Error reading file '{filename}': {e}[/red]")
            raise typer.Exit(1)

    image_digest = None
    try:
        toml_config = get_validated_config("cerebrium.toml", None, True)
    except FileNotFoundError:
        toml_config = None

    # Region priority: 1. CLI param, 2. TOML config (hardware.region), 3. default region
    region = region
    if not region and toml_config and toml_config.hardware and toml_config.hardware.region:
        region = toml_config.hardware.region
    if not region:
        region = get_default_region()

    # if toml_config, use the app name from the config
    app_name = ""
    if toml_config and toml_config.deployment.name:
        app_name = toml_config.deployment.name

    if app_name == "" or app_name is None:
        print(
            "[yellow]⚠️ No app name provided. Using the current directory name as the app name.[/yellow]"
        )
        app_name = Path(".").resolve().name

    # Check app_name length
    if len(app_name) > 30:
        print("[red]❌ Invalid app name. App names must be shorter than 30 characters.[/red]")
        raise typer.Exit(1)

    # Create the app if it doesn't exist
    app_id = f"{project_id}-{app_name}"
    create_app_response = cerebrium_request(
        http_method="POST",
        requires_auth=True,
        url=f"v3/projects/{project_id}/apps/{app_id}/create-run-app?region={region}",
    )
    if create_app_response.status_code != 200:
        print(
            f"[red]❌ Failed to create app '{app_name}' with status code {create_app_response.status_code}[/red]"
        )
        print(create_app_response.text)
        raise typer.Exit(1)

    if toml_config and (
        toml_config.dependencies.pip
        or toml_config.dependencies.conda
        or toml_config.dependencies.apt
    ):
        # Validate dependency list size (380KB limit) for cerebrium run
        deps_json = toml_config.dependencies.__json__()
        deps_for_size_check = {
            "pip": deps_json["pip"],
            "conda": deps_json["conda"],
            "apt": deps_json["apt"],
        }
        deps_json_str = json.dumps(deps_for_size_check, separators=(",", ":"))
        deps_size = len(deps_json_str.encode("utf-8"))
        max_deps_size = 380 * 1024  # 380KB in bytes

        if deps_size > max_deps_size:
            print(
                f"[red]❌ Dependency list size ({deps_size / 1024:.2f}KB) exceeds the 380KB limit for cerebrium run.[/red]"
            )
            print(
                "[yellow]💡 Consider reducing dependencies or using `cerebrium deploy` for larger dependency lists.[/yellow]"
            )
            raise typer.Exit(1)

        image_digest = create_base_image(toml_config, region)
        if not image_digest:
            print("[red]Failed to create base image[/red]")
            return typer.Exit(1)

    # Build hardware info for display and query
    hardware_info = []
    hardware_params = {}
    if toml_config and toml_config.hardware:
        if toml_config.hardware.compute:
            hardware_info.append(f"Compute: {toml_config.hardware.compute}")
            hardware_params["computeType"] = toml_config.hardware.compute
        if toml_config.hardware.gpu_count:
            hardware_info.append(f"GPU: {toml_config.hardware.gpu_count}")
            hardware_params["gpuCount"] = toml_config.hardware.gpu_count
        if toml_config.hardware.cpu:
            hardware_info.append(f"CPU: {toml_config.hardware.cpu}")
            hardware_params["cpu"] = toml_config.hardware.cpu
        if toml_config.hardware.memory:
            hardware_info.append(f"Memory: {toml_config.hardware.memory}")
            hardware_params["memoryGb"] = toml_config.hardware.memory

    hardware_display = f" ({', '.join(hardware_info)})" if hardware_info else ""

    # Create spinner for the running app process
    spinner = Spinner("dots", f"Running app: {app_name}{hardware_display}")
    live = Live(spinner, refresh_per_second=10)
    live.start()

    # Get the file list using the same logic as deploy
    if toml_config:
        file_list = determine_includes(
            include=toml_config.deployment.include,
            exclude=toml_config.deployment.exclude,
        )
    else:
        # If no config, include all files except common dev folders and dotfiles
        file_list = determine_includes(
            include=["*"],
            exclude=[".git/*", "*.pyc", "__pycache__/*", ".DS_Store", "*.swp", "*.swo", "venv"],
        )

    if not file_list:
        print("[red]❌ No files to upload. Please ensure you have files in your project.[/red]")
        raise typer.Exit(1)

    tar_path = None
    try:
        tar_path = create_tar_file(file_list, filename, needs_main_injection)

        # Validate tar file size (4MB limit)
        tar_size = os.path.getsize(tar_path)
        max_tar_size = 4 * 1024 * 1024  # 4MB in bytes
        if tar_size > max_tar_size:
            live.stop()
            if tar_path:
                try_remove_tar(tar_path)

            print(
                f"[red]❌ Tar file size ({tar_size / (1024 * 1024):.2f}MB) exceeds the 4MB limit for cerebrium run.[/red]"
            )
            print(
                "[yellow]💡 Consider using `cerebrium deploy` for larger projects or exclude unnecessary files.[/yellow]"
            )
            raise typer.Exit(1)

        # Update spinner message during upload
        spinner.text = f"Uploading app. {hardware_display}"

        # Build query string
        query = f"?filename={filename}&appName={app_name}&region={region}"
        if function_name:
            query += f"&functionName={function_name}"

        data_json = {}
        if data:
            try:
                if isinstance(data, str):
                    data_json = json.loads(data)
                else:
                    data_json = data
            except json.JSONDecodeError:
                live.stop()
                print("[red]❌ Invalid JSON data provided.[/red]")
                raise typer.Exit(1)
        elif ctx.args:
            i = 0
            while i < len(ctx.args):
                arg = ctx.args[i][2:]
                arg_split = arg.split("=", maxsplit=1)
                # arg is --key value
                if len(arg_split) == 1:
                    value = ctx.args[i + 1]
                    data_json[arg_split[0]] = value
                    i += 2
                # arg is --key=value
                else:
                    key = arg_split[0]
                    value = arg_split[1]
                    data_json[key] = value
                    i += 1

        if image_digest:
            query += f"&imageDigest={image_digest}"

        # Add hardware parameters to query
        for param, value in hardware_params.items():
            query += f"&{param}={value}"

        app_id = f"{project_id}-{app_name}"

        # Validate JSON data size (2MB limit)
        data_json_str = json.dumps(data_json)
        data_size = len(data_json_str.encode("utf-8"))
        max_data_size = 2 * 1024 * 1024  # 2MB in bytes

        if data_size > max_data_size:
            live.stop()
            if tar_path:
                try_remove_tar(tar_path)

            print(
                f"[red]❌ JSON data size ({data_size / (1024 * 1024):.2f}MB) exceeds the 2MB limit for cerebrium run.[/red]"
            )
            print("[yellow]💡 Consider reducing the data payload size.[/yellow]")
            raise typer.Exit(1)

        with open(tar_path, "rb") as tar_file:
            response = cerebrium_request(
                http_method="POST",
                requires_auth=True,
                url=f"v3/projects/{project_id}/apps/{app_id}/run{query}",
                files={
                    "data": ("data.json", StringIO(data_json_str), "application/json"),
                    "file": (os.path.basename(tar_path), tar_file, "application/x-tar"),
                },
            )

        if response.status_code != 200:
            live.stop()
            print(f"[red]❌ Upload failed with status code {response.status_code}[/red]")
            print(response.text)
            raise typer.Exit(1)

        run_id = response.json().get("runId")
        if not run_id:
            live.stop()
            print("[red]❌ No run ID returned from the server.[/red]")
            raise typer.Exit(1)

        # Stop upload spinner and show completion on same line
        live.update(
            Spinner(
                "dots",
                text=f"[green]✓ App uploaded successfully![/green] {hardware_display}",
            )
        )
        live.stop()

        # Start monitoring spinner
        monitoring_spinner = Spinner("dots", "Executing...")
        monitoring_live = Live(monitoring_spinner, refresh_per_second=10)
        monitoring_live.start()

        try:
            poll_app_logs(project_id, app_name, run_id, monitoring_live)
        finally:
            monitoring_live.stop()

    except Exception as e:
        if "live" in locals():
            live.stop()
        raise e
    finally:
        if "live" in locals():
            live.stop()
        if tar_path:
            try_remove_tar(tar_path)

    return typer.Exit(0)


def check_run_status(project_id: str, app_name: str, run_id: str):
    """
    Check the status of a run.
    Returns the status string or None if the request fails.
    """
    app_id = f"{project_id}-{app_name}"
    run_status_response = cerebrium_request(
        "GET",
        f"v2/projects/{project_id}/apps/{app_id}/runs/{run_id}",
        {},
        requires_auth=True,
    )

    if run_status_response and run_status_response.status_code == 200:
        run_data = run_status_response.json()
        return run_data.get("item", {}).get("status", "").lower()

    return None


def poll_app_logs(project_id: str, app_name: str, run_id: str, monitoring_live=None):
    """
    Polls the app logs until the run is complete.
    """
    next_token = ""

    for _ in range(60 * 15):  # Poll for up to 15 minutes
        # Check run status first
        status = check_run_status(project_id, app_name, run_id)

        # If run is complete (success or failed), stop polling after getting final logs
        if status in ["success", "failed", "fail"]:
            if status == "success":
                if monitoring_live:
                    monitoring_live.update(
                        Spinner(
                            "dots",
                            text="[green]✓ Run completed successfully.[/green] Waiting for logs. (ctrl+C to exit)",
                        )
                    )
            else:
                if monitoring_live:
                    monitoring_live.update(
                        Spinner(
                            "dots",
                            text="[red]❌ Run failed.[/red] Waiting for logs. (ctrl+C to exit)",
                        )
                    )

            for i in range(10):  # Fetch final logs a few times
                response = api.fetch_app_logs(project_id, app_name, run_id, next_token)
                next_token = response.get("nextPageToken", "")
                print_logs(response)
                time.sleep(0.5)

            if status == "success":
                if monitoring_live:
                    monitoring_live.update(
                        Spinner("dots", text="[green]✓ Run completed successfully.[/green]")
                    )
            else:
                if monitoring_live:
                    monitoring_live.update(Spinner("dots", text="[red]❌ Run failed.[/red]"))
            return

        # Get logs
        response = api.fetch_app_logs(project_id, app_name, run_id, next_token)
        next_token = response.get("nextPageToken", "")
        print_logs(response)

        time.sleep(1)

    print("[yellow]⚠️ Polling timeout reached.[/yellow]")


seen_log_ids = set()


def print_logs(response):
    for log in response["logs"]:
        if log["logId"] in seen_log_ids:
            continue
        seen_log_ids.add(log["logId"])
        formated_date = format_created_at(log["timestamp"])
        print(f"[cyan]{formated_date} {log['logLine']}[/cyan]")


def create_tar_file(file_list, filename, needs_main_injection):
    """
    Create a tar file from the given file list.

    Args:
        file_list: List of files to include in the tar
        filename: Target filename for main injection
        needs_main_injection: Whether to inject main guard into the target file

    Returns:
        str: Path to the created tar file
    """
    tar_path = None
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp_tar:
        tar_path = tmp_tar.name

        with tarfile.open(tar_path, "w") as tar:
            for file_path in file_list:
                # Convert to Path object for easier manipulation
                file_path_obj = Path(file_path)

                # Skip the tar file itself if it's in the list
                if file_path == tar_path:
                    continue

                # If this is the target file and needs main injection, create modified version
                if needs_main_injection and file_path_obj.name == filename:
                    # Read the original file
                    with open(file_path, "r", encoding="utf-8") as f:
                        original_content = f.read()

                    # Read the inject_main.py content
                    inject_main_path = Path(__file__).parent / "inject_main.py"
                    with open(inject_main_path, "r", encoding="utf-8") as f:
                        inject_content = f.read()

                    # Combine original content with inject_main.py content
                    modified_content = original_content + "\n\n" + inject_content

                    # Create a temporary file with the modified content
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".py", delete=False, encoding="utf-8"
                    ) as tmp_file:
                        tmp_file.write(modified_content)
                        tmp_file_path = tmp_file.name

                    try:
                        # Set proper file permissions before adding to tar
                        os.chmod(tmp_file_path, 0o644)
                        tar.add(tmp_file_path, arcname=file_path)
                    finally:
                        os.unlink(tmp_file_path)
                else:
                    tar.add(file_path, arcname=file_path)

    return tar_path


def try_remove_tar(tar_path):
    """
    Attempt to remove the tar file, ignoring errors if it doesn't exist.
    """
    try:
        os.remove(tar_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[red]❌ Error removing tar file: {e}[/red]")

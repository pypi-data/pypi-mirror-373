import json
import os
import struct
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from typing import Literal, Any, cast, IO, Union, Optional

import bugsnag
import requests
import typer
from rich import print
from tenacity import retry, stop_after_delay, wait_fixed
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from cerebrium import env, __version__
from cerebrium.config import CerebriumConfig
from cerebrium.context import get_or_refresh_token, get_current_project, cli_context
from cerebrium.types import JSON
from cerebrium.utils.files import detect_dev_folders
from cerebrium.utils.logging import cerebrium_log
from cerebrium.utils.sync_files import make_cortex_dep_files
from cerebrium.utils.termination import _graceful_shutdown


@retry(stop=stop_after_delay(60), wait=wait_fixed(8))
def cerebrium_request(
    http_method: Literal["GET", "POST", "DELETE", "PATCH"],
    url: str,
    payload: dict[str, JSON] = {},
    requires_auth: bool = True,
    headers: dict[str, str] = {},
    v1: bool = False,
    files: Union[dict[str, tuple[str, IO, str]], None] = None,
) -> requests.Response:
    """
    Make a request to the Cerebrium API and check the response for errors.

    Args:
        http_method ('GET', 'POST', 'DELETE'): The HTTP method to use (GET, POST or DELETE).
        url (str): The url after the base url to use.
        payload (dict, optional): The payload to send with the request.
        requires_auth (bool): If the api call requires the user to be authenticated
        headers (dict, optional): By default, content-type is application/json so this is used to override
        v1 (bool, optional): If the request is to the v1 API. Defaults to False.
        files (dict, optional): Files to send in the request, used when uploading files.

    Returns:
        dict: The response from the request.
    """
    if requires_auth:
        access_token = get_or_refresh_token()
        if not access_token:
            sys.exit(1)

        payload["projectId"] = get_current_project()

    else:
        access_token = None

    url = f"{env.values()['api_url_v1'] if v1 else env.values()['api_url_v2']}/{url}"

    # Add CLI version header to all requests
    headers["X-CLI-Version"] = __version__
    headers["X-Source"] = "cli"

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    # Check for verbose mode
    if cli_context.verbose:
        cerebrium_log(level="DEBUG", message=f"Request: {http_method} {url}", prefix="API")
        cerebrium_log(
            level="DEBUG",
            message=f"Headers: {json.dumps({k: v if k != 'Authorization' else 'Bearer ***' for k, v in headers.items()}, indent=2)}",
            prefix="API",
        )
        if payload and not files:
            cerebrium_log(
                level="DEBUG", message=f"Payload: {json.dumps(payload, indent=2)}", prefix="API"
            )

    data = None if payload is None else json.dumps(payload)
    if http_method == "POST":
        if files:
            resp = requests.post(url, headers=headers, files=files, data=payload, timeout=30)
        else:
            resp = requests.post(url, headers=headers, data=data, timeout=30)
    elif http_method == "GET":
        resp = requests.get(
            url,
            headers=headers,
            params=payload,
            timeout=30,
        )
    elif http_method == "DELETE":
        resp = requests.delete(url, headers=headers, params=payload, data=data, timeout=30)
    elif http_method == "PATCH":
        resp = requests.patch(url, headers=headers, params=payload, data=data, timeout=30)
    else:
        cerebrium_log(
            level="ERROR",
            message="Invalid HTTP method. Please use 'GET', 'POST', 'DELETE' or 'PATCH'.",
            prefix="",
        )
        bugsnag.notify(Exception("Invalid HTTP method."), severity="error")
        sys.exit(1)

    if cli_context.verbose:
        cerebrium_log(
            level="DEBUG", message=f"Response Status: {resp.status_code}", prefix="API"
        )
        cerebrium_log(
            level="DEBUG",
            message=f"Response Headers: {json.dumps(dict(resp.headers), indent=2)}",
            prefix="API",
        )
        try:
            # Try to parse JSON response for pretty printing
            response_json = resp.json()
            cerebrium_log(
                level="DEBUG",
                message=f"Response Body: {json.dumps(response_json, indent=2)}",
                prefix="API",
            )
        except:
            # If not JSON, show raw text (truncated if too long)
            body = resp.text[:1000] + "..." if len(resp.text) > 1000 else resp.text
            cerebrium_log(level="DEBUG", message=f"Response Body: {body}", prefix="API")

    if resp.status_code == 402:
        # Handle 402 Payment Required error
        message = resp.json().get(
            "message", "Payment required. Check your project plan or billing status."
        )
        cerebrium_log(
            level="ERROR",
            message=message,
            prefix="",
        )
        bugsnag.notify(Exception(message), severity="warning")
        sys.exit(1)

    return resp


# Define size limits
WARNING_SIZE_LIMIT = 1 * 1024 * 1024 * 1024  # 1GB in bytes
ERROR_SIZE_LIMIT = 2 * 1024 * 1024 * 1024  # 2GB in bytes


def upload_cortex_files(
    build_id: str,
    cerebrium_config: CerebriumConfig,
    upload_url: str,
    zip_file_name: str,
    config: CerebriumConfig,
    file_list: list[str],
    source: Literal["serve", "cortex"] = "cortex",
    disable_animation: bool = False,
) -> bool:
    if file_list == []:
        cerebrium_log(
            level="ERROR",
            message="No files to upload.",
            prefix="Error uploading app to Cerebrium:",
        )
        raise typer.Exit(1)

    # Check for development folders in the root directory
    detected_dev_folders = detect_dev_folders(file_list)
    if detected_dev_folders:
        folders_str = ", ".join(f"'{folder}'" for folder in detected_dev_folders)
        cerebrium_log(
            level="WARNING",
            message=f"Development folder(s) {folders_str} detected in the root directory. "
            f"Including development folders is not recommended as they can significantly "
            f"increase upload size. They can be excluded in the cerebrium.toml file.",
            prefix="Warning:",
        )

    def add_utc_timestamp(zip_info: zipfile.ZipInfo, dt: datetime) -> None:
        # Convert the timezone-aware datetime to a Unix timestamp (UTC)
        timestamp = int(dt.timestamp())
        # Build the extra field: header ID 0x5455, data length 5, flag 1, then 4 bytes of timestamp.
        extra_field = struct.pack("<HHBI", 0x5455, 5, 1, timestamp)
        zip_info.extra = extra_field

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, zip_file_name)
            make_cortex_dep_files(working_dir=temp_dir, config=config)
            tmp_dep_files = os.listdir(temp_dir)
            with zipfile.ZipFile(zip_path, "w") as zip_file:
                print(f"Zipping {len(file_list)} file(s)...")

                # Process temporary dependency files.
                for f in tmp_dep_files:
                    full_path = os.path.join(temp_dir, f)
                    st = os.stat(full_path)
                    dt = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                    # Use the file name relative to the temp directory.
                    zi = zipfile.ZipInfo(f, date_time=time.gmtime(st.st_mtime)[:6])
                    add_utc_timestamp(zi, dt)
                    if os.path.isfile(full_path):
                        with open(full_path, "rb") as fp:
                            file_data = fp.read()
                        zip_file.writestr(zi, file_data)
                    elif os.path.isdir(full_path):
                        zip_file.writestr(zi, b"")

                # Process files from file_list.
                for f in file_list:
                    # Skip files already added from the temporary directory.
                    if f in tmp_dep_files:
                        continue
                    if os.path.isfile(f):
                        st = os.stat(f)
                        dt = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                        # Use the full relative path to preserve folder structure.
                        zi = zipfile.ZipInfo(f, date_time=time.gmtime(st.st_mtime)[:6])
                        add_utc_timestamp(zi, dt)
                        with open(f, "rb") as fp:
                            file_data = fp.read()
                        zip_file.writestr(zi, file_data)
                    elif os.path.isdir(f) and len(os.listdir(f)) == 0:
                        st = os.stat(f)
                        dt = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                        zi = zipfile.ZipInfo(f, date_time=time.gmtime(st.st_mtime)[:6])
                        add_utc_timestamp(zi, dt)
                        zip_file.writestr(zi, b"")

            # Check the zip file size
            zip_size = os.path.getsize(zip_path)
            if zip_size > ERROR_SIZE_LIMIT:
                cerebrium_log(
                    level="ERROR",
                    message="Your project zip file is over 2GB. Please use the cerebrium cp command to upload files instead.",
                    prefix="Error uploading app to Cerebrium:",
                )
                bugsnag.notify(Exception("Zip file is over 2GB"), severity="warning")
                raise typer.Exit(1)
            elif zip_size > WARNING_SIZE_LIMIT:
                cerebrium_log(
                    level="WARNING",
                    message="Your project zip file is over 1GB. Your deployment should work but might encounter issues. Please consider using the cerebrium cp command if you encounter issues.",
                    prefix="Warning:",
                )
                bugsnag.notify(Exception("Zip file is over 1GB"), severity="warning")
            print("Uploading to Cerebrium...")

            with open(zip_path, "rb") as f:
                headers = {"Content-Type": "application/zip"}
                if not disable_animation:
                    with tqdm(
                        total=zip_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        colour="#EB3A6F",
                        ncols=100,
                    ) as pbar:
                        wrapped_f = CallbackIOWrapper(pbar.update, f, "read")
                        upload_response = requests.put(
                            upload_url,
                            headers=headers,
                            data=cast(IO[bytes], wrapped_f),
                            timeout=60,
                        )
                else:
                    upload_response = requests.put(
                        upload_url, headers=headers, data=f, timeout=60
                    )

            if upload_response.status_code != 200:
                bugsnag.notify(
                    Exception(f"Error uploading app to Cerebrium\n{upload_response.json()}"),
                    severity="error",
                )
                cerebrium_log(
                    level="ERROR",
                    message=f"Error uploading app to Cerebrium\n{upload_response.json().get('message')}",
                    prefix="",
                )
                raise typer.Exit(1)
            if source == "cortex":
                print("Resources uploaded successfully.")
            return True

    except KeyboardInterrupt:
        _graceful_shutdown(
            app_name=cerebrium_config.deployment.name,
            build_id=build_id,
            is_interrupt=True,
        )
        raise typer.Exit(1)


# Function to get the logs from the API
def fetch_build_logs(app_name: str, build_id: str) -> dict[str, Any]:
    """
    Fetches the build logs from the API.

    Args:
        app_name (str): The app name.
        build_id (str): The build ID.

    Returns:
        dict: The response JSON containing the logs and build status.
    """
    project_id = get_current_project()

    response = cerebrium_request(
        "GET",
        f"v2/projects/{project_id}/apps/{project_id}-{app_name}/builds/{build_id}/logs",
        {},
    )

    if response is None or response.status_code != 200:
        if response is None:
            error_message = "Error streaming logs. Please check your internet connection. If this issue persists, please contact support."
        else:
            try:
                error_data = response.json()
                error_message = (
                    f"Error streaming logs\n{error_data.get('message', 'Unknown error')}"
                )
            except Exception:
                error_message = (
                    f"Error streaming logs (status {response.status_code}): {response.text}"
                )

        cerebrium_log(level="ERROR", message=error_message, prefix="")
        bugsnag.notify(Exception(error_message), severity="error")
        raise typer.Exit(1)

    return response.json()


def fetch_app_logs(
    project_id: str, app_name: str, run_id: str, next_token: str
) -> dict[str, Any]:
    """
    Fetches the app logs from the API.

    Args:
        project_id (str): The project ID.
        app_name (str): The app name.
        run_id (str): The run ID.
        next_token (str): The token for the next set of logs, if any.

    Returns:
        dict: The response JSON containing the logs and run status.
    """

    url = f"v2/projects/{project_id}/apps/{project_id}-{app_name}/logs?runId={run_id}&direction=forward"

    if next_token:
        url += f"&nextToken={next_token}"

    response = cerebrium_request(
        "GET",
        url,
        {},
    )

    if response is None or response.status_code != 200:
        if response is None:
            error_message = "Error streaming logs. Please check your internet connection. If this issue persists, please contact support."
        else:
            try:
                error_data = response.json()
                error_message = (
                    f"Error streaming logs\n{error_data.get('message', 'Unknown error')}"
                )
            except Exception:
                error_message = (
                    f"Error streaming logs (status {response.status_code}): {response.text}"
                )

        cerebrium_log(level="ERROR", message=error_message, prefix="")
        bugsnag.notify(Exception(error_message), severity="error")
        raise typer.Exit(1)

    return response.json()


def fetch_notifications() -> list[dict[str, Any]]:
    """
    Fetches notifications from the API.

    Returns:
        list: The list of notifications
    """
    try:
        response = cerebrium_request("GET", f"v2/notifications", {}, requires_auth=False)

        if response and response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception:
        return []

import base64
import time
from typing import Optional

from cerebrium.api import cerebrium_request
from cerebrium.config import CerebriumConfig
from cerebrium.types import JSON
from cerebrium.utils.deploy import poll_build_logs
from cerebrium.utils.logging import cerebrium_log
from cerebrium.context import get_current_project


def encode_base64(commands: list[str]) -> list[str]:
    return [base64.b64encode(cmd.encode()).decode() for cmd in commands]


def create_base_image(config: CerebriumConfig, region: str) -> Optional[str]:
    payload: dict[str, JSON] = {
        "dependencies": config.dependencies.__json__(),
        "preBuildCommands": encode_base64(config.deployment.pre_build_commands),
        "shellCommands": encode_base64(config.deployment.shell_commands),
        "baseImageURI": config.deployment.docker_base_image_url,
    }

    project_id = get_current_project()
    app_id = f"{project_id}-{config.deployment.name}"
    max_attempts = 10

    def request_and_log_status() -> tuple[Optional[str], Optional[str]]:
        try:
            response = cerebrium_request(
                "POST",
                f"v3/projects/{project_id}/apps/{app_id}/base-image?region={region}",
                payload,
                requires_auth=True,
            )
            if response.status_code != 200:
                cerebrium_log(
                    level="ERROR",
                    message=f"Base image request failed with code {response.status_code}",
                    prefix="",
                )
                cerebrium_log(
                    level="ERROR",
                    message=f"Response: {response.text}",
                    prefix="",
                )
                return None, None

            result = response.json()
            return result.get("status"), result.get("digest")
        except Exception as e:
            cerebrium_log(level="ERROR", message=f"Request error: {e}", prefix="")
            return None, None

    for attempt in range(max_attempts):
        status, image_digest = request_and_log_status()

        if status is None:
            return None

        if status == "ready" and image_digest:
            return image_digest

        time.sleep(2)
        poll_build_logs(
            image_digest or "unknown",
            deployment_name=config.deployment.name,
            build_status="pending",
            build_type="Base Image",
        )

    cerebrium_log(
        level="ERROR",
        message=f"❌ Base image not ready after {max_attempts} attempts",
        prefix="",
    )
    return None

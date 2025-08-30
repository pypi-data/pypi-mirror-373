import os
from abc import abstractmethod
from typing import Any, Optional

import bugsnag
import toml
import typer
from atom.api import Atom

from cerebrium.defaults import (
    DISABLE_AUTH,
    DOCKER_BASE_IMAGE_URL,
    ENTRYPOINT,
    EXCLUDE,
    HEALTHCHECK_ENDPOINT,
    READYCHECK_ENDPOINT,
    INCLUDE,
    PORT,
    PRE_BUILD_COMMANDS,
    PYTHON_VERSION,
    SHELL_COMMANDS,
    DOCKERFILE_PATH,
)
from cerebrium.utils.logging import cerebrium_log


class TOMLConfig(Atom):
    @abstractmethod
    def __toml__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __json__(self) -> dict:
        raise NotImplementedError


class ScalingConfig(TOMLConfig):
    min_replicas: Optional[int] = None
    max_replicas: Optional[int] = None
    cooldown: Optional[int] = None
    replica_concurrency: Optional[int] = None
    response_grace_period: Optional[int] = None
    scaling_metric: Optional[str] = None
    scaling_target: Optional[int] = None
    scaling_buffer: Optional[int] = None
    roll_out_duration_seconds: Optional[int] = None

    def __toml__(self) -> str:
        lines = ["[cerebrium.scaling]"]
        if self.min_replicas is not None:
            lines.append(f"min_replicas = {self.min_replicas}")
        if self.max_replicas is not None:
            lines.append(f"max_replicas = {self.max_replicas}")
        if self.cooldown is not None:
            lines.append(f"cooldown = {self.cooldown}")
        if self.replica_concurrency is not None:
            lines.append(f"replica_concurrency = {self.replica_concurrency}")
        if self.response_grace_period is not None:
            lines.append(f"response_grace_period = {self.response_grace_period}")
        if self.scaling_metric is not None:
            lines.append(f'scaling_metric = "{self.scaling_metric}"')
        if self.scaling_target is not None:
            lines.append(f"scaling_target = {self.scaling_target}")
        if self.scaling_buffer is not None:
            lines.append(f"scaling_buffer = {self.scaling_buffer}")
        if self.roll_out_duration_seconds is not None:
            lines.append(f"roll_out_duration_seconds = {self.roll_out_duration_seconds}")
        return "\n".join(lines) + "\n\n"

    def __json__(self) -> dict:
        result = {}
        if self.min_replicas is not None:
            result["minReplicaCount"] = self.min_replicas
        if self.max_replicas is not None:
            result["maxReplicaCount"] = self.max_replicas
        if self.cooldown is not None:
            result["cooldownPeriodSeconds"] = self.cooldown
        if self.replica_concurrency is not None:
            result["replicaConcurrency"] = self.replica_concurrency
        if self.response_grace_period is not None:
            result["responseGracePeriodSeconds"] = self.response_grace_period
        if self.scaling_metric is not None:
            result["scalingMetric"] = self.scaling_metric
        if self.scaling_target is not None:
            result["scalingTarget"] = self.scaling_target
        if self.scaling_buffer is not None:
            result["scalingBuffer"] = self.scaling_buffer
        if self.roll_out_duration_seconds is not None:
            result["rollOutDurationSeconds"] = self.roll_out_duration_seconds
        return result


class HardwareConfig(TOMLConfig):
    cpu: Optional[float] = None
    memory: Optional[float] = None
    compute: Optional[str] = None
    gpu_count: Optional[int] = None
    provider: Optional[str] = None
    region: Optional[str] = None

    def __init__(self, **kwargs):
        # Check if gpu_count was explicitly provided in the config
        gpu_count_provided = "gpu_count" in kwargs

        # Convert cpu and memory to float if they're provided as int
        if "cpu" in kwargs and kwargs["cpu"] is not None:
            kwargs["cpu"] = float(kwargs["cpu"])
        if "memory" in kwargs and kwargs["memory"] is not None:
            kwargs["memory"] = float(kwargs["memory"])

        super().__init__(**kwargs)
        # Default gpu_count to 1 if not explicitly set and compute is not CPU
        if self.compute is not None and self.compute != "CPU" and not gpu_count_provided:
            self.gpu_count = 1

    def __toml__(self) -> str:
        lines = ["[cerebrium.hardware]"]
        if self.cpu is not None:
            lines.append(f"cpu = {self.cpu}")
        if self.memory is not None:
            lines.append(f"memory = {self.memory}")
        if self.compute is not None:
            lines.append(f'compute = "{self.compute}"')
        if self.gpu_count is not None and self.compute is not None and self.compute != "CPU":
            lines.append(f"gpu_count = {self.gpu_count}")
        if self.provider is not None:
            lines.append(f'provider = "{self.provider}"')
        if self.region is not None:
            lines.append(f'region = "{self.region}"')
        return "\n".join(lines) + "\n\n"

    def __json__(self) -> dict:
        result = {}
        if self.cpu is not None:
            result["cpu"] = self.cpu
        if self.memory is not None:
            result["memory"] = self.memory
        if self.compute is not None:
            result["compute"] = self.compute
        if self.gpu_count is not None and self.compute != "CPU":
            result["gpuCount"] = self.gpu_count
        if self.provider is not None:
            result["provider"] = self.provider
        if self.region is not None:
            result["region"] = self.region
        return result


class CustomRuntimeConfig(TOMLConfig):
    entrypoint: list[str] = ENTRYPOINT
    port: int = PORT
    healthcheck_endpoint: str = HEALTHCHECK_ENDPOINT
    readycheck_endpoint: str = READYCHECK_ENDPOINT
    dockerfile_path: str = DOCKERFILE_PATH

    def __toml__(self) -> str:
        return (
            "[cerebrium.runtime.custom]\n"
            f"entrypoint = {self.entrypoint}\n"
            f'port = "{self.port}"\n'
            f'healthcheck_endpoint = "{self.healthcheck_endpoint}"\n'
            f'readycheck_endpoint = "{self.readycheck_endpoint}"\n'
            f'dockerfile_path = "{self.dockerfile_path}"\n\n'
        )

    def __json__(self) -> dict:
        return {
            "entrypoint": (
                self.entrypoint
                if isinstance(self.entrypoint, list)
                else self.entrypoint.split()
            ),
            "port": self.port,
            "healthcheckEndpoint": self.healthcheck_endpoint,
            "readycheckEndpoint": self.readycheck_endpoint,
            "dockerfilePath": self.dockerfile_path,
        }


class DeploymentConfig(TOMLConfig):
    name: str
    python_version: str = PYTHON_VERSION
    docker_base_image_url: str = DOCKER_BASE_IMAGE_URL
    include: list[str] = INCLUDE
    exclude: list[str] = EXCLUDE
    shell_commands: list[str] = SHELL_COMMANDS
    pre_build_commands: list[str] = PRE_BUILD_COMMANDS
    disable_auth: bool = DISABLE_AUTH

    def __toml__(self) -> str:
        shell_commands = (
            f"shell_commands = {self.shell_commands}\n" if self.shell_commands else ""
        )

        return (
            "[cerebrium.deployment]\n"
            f'name = "{self.name}"\n'
            f'python_version = "{self.python_version}"\n'
            f'docker_base_image_url = "{self.docker_base_image_url}"\n'
            f"disable_auth = {str(self.disable_auth).lower()}\n"
            f"include = {self.include}\n"
            f"exclude = {self.exclude}\n" + shell_commands + "\n"
        )

    def __json__(self) -> dict:
        return {
            "name": self.name,
            "pythonVersion": self.python_version,
            "baseImage": self.docker_base_image_url,
            "include": self.include,
            "exclude": self.exclude,
            "shellCommands": self.shell_commands,
            "preBuildCommands": self.pre_build_commands,
            "disableAuth": self.disable_auth,
        }


class DependencyConfig(Atom):
    pip: dict[str, str] = {}
    conda: dict[str, str] = {}
    apt: dict[str, str] = {}

    paths: dict[str, str] = {"pip": "", "conda": "", "apt": ""}

    def __toml__(self) -> str:
        pip_strings = (
            "[cerebrium.dependencies.pip]\n"
            + "\n".join(f'"{key}" = "{value}"' for key, value in self.pip.items())
            + "\n"
            if self.pip
            else ""
        )
        conda_strings = (
            "[cerebrium.dependencies.conda]\n"
            + "\n".join(f'"{key}" = "{value}"' for key, value in self.conda.items())
            + "\n"
            if self.conda != {}
            else ""
        )
        apt_strings = (
            "[cerebrium.dependencies.apt]\n"
            + "\n".join(f'"{key}" = "{value}"' for key, value in self.apt.items())
            + "\n"
            if self.apt != {}
            else ""
        )
        if pip_strings or conda_strings or apt_strings:
            return pip_strings + conda_strings + apt_strings + "\n"
        return ""

    def __json__(self) -> dict:
        from cerebrium.utils.requirements import parse_requirements
        import os

        # Convert file paths to actual dependencies if files are specified
        pip_deps = self.pip.copy()
        conda_deps = self.conda.copy()
        apt_deps = self.apt.copy()

        # If file paths are specified, read and merge the contents
        if self.paths.get("pip") and os.path.exists(self.paths["pip"]):
            file_deps = parse_requirements(self.paths["pip"])
            pip_deps.update(file_deps)

        if self.paths.get("conda") and os.path.exists(self.paths["conda"]):
            file_deps = parse_requirements(self.paths["conda"])
            conda_deps.update(file_deps)

        if self.paths.get("apt") and os.path.exists(self.paths["apt"]):
            file_deps = parse_requirements(self.paths["apt"])
            apt_deps.update(file_deps)

        return {
            "pip": pip_deps,
            "conda": conda_deps,
            "apt": apt_deps,
            "pip_file": self.paths["pip"],
            "conda_file": self.paths["conda"],
            "apt_file": self.paths["apt"],
        }


class PartnerConfig(TOMLConfig):
    name: str
    port: int | None = None

    def __toml__(self) -> str:
        toml_str = "[cerebrium.partner.service]\n" f'name = "{self.name}"\n'
        if self.port is not None:
            toml_str += f"port = {self.port}\n"
        toml_str += "\n"
        return toml_str

    def __json__(self) -> dict[str, Any]:
        result: dict[str, Any] = {"partnerName": self.name}
        if self.port is not None:
            result["port"] = self.port
        return result


class CerebriumConfig(Atom):
    deployment: DeploymentConfig
    hardware: HardwareConfig
    scaling: ScalingConfig
    dependencies: DependencyConfig
    custom_runtime: CustomRuntimeConfig | None = None
    partner_services: PartnerConfig | None = None

    def to_toml(self, file: str = "cerebrium.toml") -> None:
        with open(file, "w", newline="\n") as f:
            f.write(self.deployment.__toml__())
            f.write(self.hardware.__toml__())
            f.write(self.scaling.__toml__())
            if self.custom_runtime is not None:
                f.write(self.custom_runtime.__toml__())
            f.write(self.dependencies.__toml__())

    def to_payload(self) -> dict:
        payload = {
            **self.deployment.__json__(),
            **self.hardware.__json__(),
            **self.scaling.__json__(),
        }
        # If user specifies partner service + port
        if self.custom_runtime is not None and self.partner_services is not None:
            payload.update(self.custom_runtime.__json__())
            payload["partnerService"] = self.partner_services.name
            payload["runtime"] = self.partner_services.name
        elif self.custom_runtime is not None:
            payload.update(self.custom_runtime.__json__())
            payload["runtime"] = "custom"
        elif self.partner_services is not None:
            payload["partnerService"] = self.partner_services.name
            payload["runtime"] = self.partner_services.name
            if self.partner_services.port is not None:
                payload["port"] = self.partner_services.port
        else:
            payload["runtime"] = "cortex"
        return payload


def get_validated_config(config_file: str, name: Optional[str], quiet: bool) -> CerebriumConfig:
    try:
        toml_config = toml.load(config_file)["cerebrium"]
    except FileNotFoundError:
        if quiet:
            raise FileNotFoundError(f"Config file {config_file} not found")

        cerebrium_log(
            message=f"Could not find {config_file} file. Please run `cerebrium init` to create one.",
            color="red",
        )
        bugsnag.notify(
            Exception(
                f"Could not find {config_file} file. Please run `cerebrium init` to create one."
            ),
            severity="warning",
        )
        raise typer.Exit(1)
    except KeyError:
        cerebrium_log(
            message=f"Could not find 'cerebrium' key in {config_file} file. Please run `cerebrium init` to create one.",
            color="red",
        )
        raise typer.Exit(1)
    except Exception as e:
        bugsnag.notify(e, severity="error")
        cerebrium_log(message=f"Error loading {config_file} file: {e}", color="red")
        raise typer.Exit(1)

    deployment_section = toml_config.get("deployment", {})
    hardware_section = toml_config.get("hardware", {})
    config_error = False

    if not deployment_section:
        cerebrium_log(
            message=f"Deployment section is required in {config_file} file. Please add a 'deployment' section.",
            level="ERROR",
        )
        config_error = True
    if "name" not in deployment_section:
        cerebrium_log(
            message=f"`deployment.name` is required in {config_file} file. Please add a 'name' field to the 'deployment' section.",
            level="ERROR",
        )
        config_error = True
    if "gpu" in hardware_section:
        cerebrium_log(
            message="`hardware.gpu` field is deprecated. Please use `hardware.compute` instead.",
            level="ERROR",
        )
        config_error = True
    if "cuda_version" in deployment_section:
        cerebrium_log(
            message="`deployment.cuda_version` field is deprecated. Please use `deployment.docker_base_image_url` instead.",
            level="ERROR",
        )
        config_error = True
    if hardware_section.get("provider", "aws") == "coreweave":
        cerebrium_log(
            message="Cortex V4 does not support Coreweave. Please consider updating your app to AWS.",
            level="ERROR",
        )
        config_error = True
    if config_error:
        raise typer.Exit(1)

    if name:
        deployment_section["name"] = name

    deployment_config = DeploymentConfig(**deployment_section)
    scaling_config = ScalingConfig(**toml_config.get("scaling", {}))
    hardware_config = HardwareConfig(**hardware_section)

    custom_runtime_config = None
    if "runtime" in toml_config and "custom" in toml_config["runtime"]:
        if "entrypoint" in toml_config["runtime"]["custom"] and isinstance(
            toml_config["runtime"]["custom"]["entrypoint"], str
        ):
            toml_config["runtime"]["custom"]["entrypoint"] = toml_config["runtime"]["custom"][
                "entrypoint"
            ].split()
        if (
            "dockerfile_path" in toml_config["runtime"]["custom"]
            and toml_config["runtime"]["custom"]["dockerfile_path"] != ""
            and not os.path.exists(toml_config["runtime"]["custom"]["dockerfile_path"])
        ):
            cerebrium_log(
                message="Dockerfile path does not exist. Please check the path in the toml file.",
                color="red",
            )
            raise typer.Exit(1)
        custom_runtime_config = CustomRuntimeConfig(**toml_config["runtime"]["custom"])

    dependency_config = DependencyConfig(**toml_config.get("dependencies", {}))

    partner_config = None
    for partner in ["deepgram", "rime"]:
        if "runtime" in toml_config and partner in toml_config["runtime"]:
            partner_data = toml_config["runtime"][partner]
            if isinstance(partner_data, dict):
                port = partner_data.get("port")
                partner_config = PartnerConfig(name=partner, port=port)
            else:
                partner_config = PartnerConfig(name=partner)

    return CerebriumConfig(
        scaling=scaling_config,
        hardware=hardware_config,
        deployment=deployment_config,
        dependencies=dependency_config,
        custom_runtime=custom_runtime_config,
        partner_services=partner_config,
    )

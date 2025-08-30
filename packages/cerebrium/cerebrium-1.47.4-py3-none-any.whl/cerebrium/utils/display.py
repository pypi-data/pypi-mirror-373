import json

import typer
from rich import box, print as console
from rich import print
from rich.panel import Panel
from rich.table import Table

from cerebrium.config import CerebriumConfig
from cerebrium.utils import requirements


def dict_pretty_print(ugly: dict | list | str) -> str:
    max_len = 200
    if isinstance(ugly, dict):
        for key, value in ugly.items():
            try:
                stringified = str(value)
                if len(stringified) > max_len:
                    ugly[key] = stringified[:max_len] + "..."
            except Exception:
                ugly[key] = "<Unable to stringify>"
        try:
            # json dump and strip the outer brackets
            pretty = json.dumps(ugly, indent=4)[1:-1]
        except Exception:
            pretty = str(ugly)
    elif isinstance(ugly, list):
        pretty = "["
        for u in ugly:
            try:
                stringified = str(u)
                if len(stringified) > max_len:
                    pretty += stringified[:max_len] + "..." + ", "
            except Exception:
                pretty += "<Unable to stringify>" + ", "
        pretty += "]"
    else:
        pretty = str(ugly)
        if len(pretty) > max_len:
            pretty = pretty[:max_len] + "..."

    return pretty


def confirm_deployment(
    config: CerebriumConfig,
):
    """
    Print out a confirmation message for the deployment
    - Display selected hardware options and configuration on a panel
    - Ask user to confirm
    """
    hardware = config.hardware
    deployment = config.deployment
    scaling = config.scaling
    dependencies = config.dependencies
    custom_runtime = config.custom_runtime

    deployment_table = Table(box=box.SIMPLE_HEAD)
    deployment_table.add_column("Parameter", style="")
    deployment_table.add_column("Value", style="")

    # TODO this needs to be converted to auto display
    deployment_table.add_row("HARDWARE PARAMETERS", "", style="bold")
    deployment_table.add_row("Compute", str(hardware.compute))
    deployment_table.add_row("CPU", str(hardware.cpu))
    deployment_table.add_row("Memory", str(hardware.memory))
    if hardware.compute != "CPU":
        deployment_table.add_row("GPU Count", str(hardware.gpu_count))

    # NOTE Do we want to display these?
    deployment_table.add_row("Region", str(hardware.region))
    deployment_table.add_row("Provider", str(hardware.provider))

    deployment_table.add_row("", "")
    deployment_table.add_row("DEPLOYMENT PARAMETERS", "", style="bold")

    # Check if using custom runtime
    if custom_runtime is not None:
        if custom_runtime.dockerfile_path:
            deployment_table.add_row("Runtime", "Custom (Dockerfile)")
            deployment_table.add_row("Dockerfile Path", str(custom_runtime.dockerfile_path))
        else:
            deployment_table.add_row("Runtime", "Custom")
            deployment_table.add_row("Python Version", str(deployment.python_version))
            deployment_table.add_row("Base Image", str(deployment.docker_base_image_url))

        deployment_table.add_row("Entrypoint", " ".join(custom_runtime.entrypoint))
        deployment_table.add_row("Port", str(custom_runtime.port))
        deployment_table.add_row(
            "Healthcheck Endpoint", str(custom_runtime.healthcheck_endpoint)
        )
        deployment_table.add_row("Readycheck Endpoint", str(custom_runtime.readycheck_endpoint))
    else:
        # Show standard Cortex runtime parameters
        deployment_table.add_row("Runtime", "Cortex")
        deployment_table.add_row("Python Version", str(deployment.python_version))
        deployment_table.add_row("Base Image", str(deployment.docker_base_image_url))

    # Always show include/exclude patterns
    deployment_table.add_row("Include Pattern", str(deployment.include))
    deployment_table.add_row("Exclude Pattern", str(deployment.exclude))

    deployment_table.add_row("", "")
    deployment_table.add_row("SCALING PARAMETERS", "", style="bold")
    deployment_table.add_row("Cooldown", str(scaling.cooldown))
    deployment_table.add_row("Minimum Replicas", str(scaling.min_replicas))
    if scaling.max_replicas is not None:
        deployment_table.add_row("Maximum Replicas", str(scaling.max_replicas))
    if scaling.replica_concurrency is not None:
        replica_concurrency_value = str(scaling.replica_concurrency)
        if hardware.compute != "CPU" and scaling.replica_concurrency > 1:
            replica_concurrency_value += " ⚠️  [yellow](GPU workloads typically perform best with concurrency 1, unless using batching. Learn more: https://docs.cerebrium.ai/cerebrium/scaling/scaling-apps#replica-concurrency)[/yellow]"
        deployment_table.add_row("Replica Concurrency", replica_concurrency_value)

    # Only show dependencies when not using a Dockerfile (dependencies are managed in Dockerfile)
    if custom_runtime is None or not custom_runtime.dockerfile_path:
        # Check if there are any dependencies to display
        has_any_deps = bool(dependencies.pip or dependencies.apt or dependencies.conda)
        
        if has_any_deps:
            deployment_table.add_row("", "")
            deployment_table.add_row("DEPENDENCIES", "", style="bold")
            
            if dependencies.pip:
                pip_deps = "".join(requirements.req_dict_to_str_list(dependencies.pip, for_display=True))
                deployment_table.add_row("pip", pip_deps)
            if dependencies.apt:
                apt_deps = "".join(requirements.req_dict_to_str_list(dependencies.apt, for_display=True))
                deployment_table.add_row("apt", apt_deps)
            if dependencies.conda:
                conda_deps = "".join(requirements.req_dict_to_str_list(dependencies.conda, for_display=True))
                deployment_table.add_row("conda", conda_deps)

    name = deployment.name
    config_options_panel = Panel.fit(
        deployment_table,
        title=f"[bold] Deployment parameters for {name} ",
        border_style="yellow bold",
        width=140,
    )
    print()
    console(config_options_panel)
    print()
    return typer.confirm(
        "Do you want to continue with the deployment?",
        default=True,
        show_default=True,
    )


def confirm_partner_service_deployment(
    config: CerebriumConfig,
):
    """
    Print out a confirmation message for the deployment
    - Display selected hardware options and configuration on a panel
    - Ask user to confirm
    """
    hardware = config.hardware
    deployment = config.deployment
    scaling = config.scaling

    deployment_table = Table(box=box.SIMPLE_HEAD)
    deployment_table.add_column("Parameter", style="")
    deployment_table.add_column("Value", style="")

    # TODO this needs to be converted to auto display
    deployment_table.add_row("HARDWARE PARAMETERS", "", style="bold")
    deployment_table.add_row("Compute", str(hardware.compute))
    deployment_table.add_row("CPU", str(hardware.cpu))
    deployment_table.add_row("Memory", str(hardware.memory))
    if hardware.compute != "CPU":
        deployment_table.add_row("GPU Count", str(hardware.gpu_count))

    # NOTE Do we want to display these?
    deployment_table.add_row("Region", str(hardware.region))
    deployment_table.add_row("Provider", str(hardware.provider))

    deployment_table.add_row("", "")
    deployment_table.add_row("SCALING PARAMETERS", "", style="bold")
    deployment_table.add_row("Cooldown", str(scaling.cooldown))
    deployment_table.add_row("Minimum Replicas", str(scaling.min_replicas))
    if scaling.max_replicas is not None:
        deployment_table.add_row("Maximum Replicas", str(scaling.max_replicas))
    if scaling.replica_concurrency is not None:
        replica_concurrency_value = str(scaling.replica_concurrency)
        if hardware.compute != "CPU" and scaling.replica_concurrency > 1:
            replica_concurrency_value += " ⚠️  [yellow](GPU workloads typically perform best with concurrency 1, unless using batching. Learn more: https://docs.cerebrium.ai/cerebrium/scaling/scaling-apps#replica-concurrency)[/yellow]"
        deployment_table.add_row("Replica Concurrency", replica_concurrency_value)

    name = deployment.name
    config_options_panel = Panel.fit(
        deployment_table,
        title=f"[bold] Deployment parameters for {name} ",
        border_style="yellow bold",
        width=140,
    )
    print()
    console(config_options_panel)
    print()
    return typer.confirm(
        "Do you want to continue with the deployment?",
        default=True,
        show_default=True,
    )


def colorise_status_for_rich(status: str) -> str:
    """Takes a status, returns a rich markup string with the correct color"""
    status = " ".join([s.capitalize() for s in status.split("_")])
    color = None
    if status == "Active":
        color = "green"
    elif status == "Cold":
        color = "bright_cyan"
    elif status == "Pending":
        color = "yellow"
    elif status == "Deploying":
        color = "bright_magenta"
    elif "error" in status.lower():
        color = "red"

    if color:
        return f"[bold {color}]{status}[bold /{color}]"
    else:
        return f"[bold]{status}[bold]"


def pretty_timestamp(timestamp: str) -> str:
    """Converts a timestamp from 2023-11-13T20:57:12.640Z to human-readable format"""
    return timestamp.replace("T", " ").replace("Z", "").split(".")[0]

import cProfile
import os
import sys
from pstats import Stats
from typing import Annotated, Optional

import bugsnag
import toml
import typer
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from cerebrium import api, __version__
from cerebrium.api import cerebrium_request
from cerebrium.config import (
    CerebriumConfig,
    ScalingConfig,
    HardwareConfig,
    DeploymentConfig,
    DependencyConfig,
    CustomRuntimeConfig,
    PartnerConfig,
)
from cerebrium.utils.check_cli_version import print_update_cli_message
from cerebrium.utils.deploy import package_app, get_function_names
from cerebrium.utils.display import confirm_partner_service_deployment
from cerebrium.utils.logging import cerebrium_log, console
from cerebrium.context import get_current_project

_EXAMPLE_MAIN = """
def run(prompt: str):
    print(f"Running on Cerebrium: {prompt}")

    return {"my_result": prompt}

# To run your app, run:
# cerebrium run main.py::run --prompt "Hello World!"
#
# To deploy your app, run:
# cerebrium deploy
"""

cortex_cli = typer.Typer(no_args_is_help=True)


@cortex_cli.command("init")
def init(
    name: Annotated[str, typer.Argument(help="Name of the Cortex deployment.")],
    dir: Annotated[str, typer.Option(help="Directory to create the Cortex deployment.")] = "./",
):
    """
    Initialize an empty Cerebrium Cortex project.
    """
    path = os.path.join(dir, name)
    toml_path = os.path.join(path, "cerebrium.toml")
    main_path = os.path.join(path, "main.py")
    if dir != "./":
        console.print(f"Initializing Cerebrium Cortex project in new directory {name}")
    else:
        console.print(f"Initializing Cerebrium Cortex project in directory {path}")

    print_update_cli_message()

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        cerebrium_log(
            level="WARNING",
            message="Directory already exists. Please choose a different name.",
            prefix_separator="\t",
        )
        bugsnag.notify(Exception("Directory already exists error."), severity="warning")
        raise typer.Exit(1)

    if not os.path.exists(main_path):
        with open(main_path, "w", newline="\n") as f:
            f.write(_EXAMPLE_MAIN)

    # Create config with sensible defaults for init
    scaling_config = ScalingConfig(
        min_replicas=0,
        max_replicas=2,
        cooldown=30,
        replica_concurrency=1,
        scaling_metric="concurrency_utilization",
    )
    hardware_config = HardwareConfig(
        cpu=2.0,
        memory=2.0,
        compute="CPU",
        gpu_count=0,
        provider="aws",
        region="us-east-1",
    )
    dependency_config = DependencyConfig()
    deployment_config = DeploymentConfig(name=name)
    config = CerebriumConfig(
        scaling=scaling_config,
        hardware=hardware_config,
        deployment=deployment_config,
        dependencies=dependency_config,
        custom_runtime=None,
    )
    config.to_toml(toml_path)
    console.print("Cerebrium Cortex project initialized successfully!")
    console.print(f"cd {path} && cerebrium deploy to get started")

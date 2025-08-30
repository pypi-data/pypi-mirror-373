from typing import Annotated

import typer
from rich import print

from cerebrium.context import get_default_region, set_default_region

region_cli = typer.Typer(no_args_is_help=True)


@region_cli.command("get")
def get_region():
    """
    Get the current default region
    """
    current_region = get_default_region()
    print(f"Default region: {current_region}")


@region_cli.command("set")
def set_region(
    region: Annotated[
        str,
        typer.Argument(
            help="The region to set as default (e.g., 'us-east-1', 'eu-west-1')",
        ),
    ],
):
    """
    Set the default region for storage operations.
    """
    if not region.strip():
        print("Error: Region cannot be empty")
        raise typer.Exit(1)

    set_default_region(region.strip())

    print(f"Default region successfully set to: {region.strip()}")

import os

from cerebrium.config import CerebriumConfig
from cerebrium.files import (
    PIP_REQUIREMENTS_FILE,
    CONDA_REQUIREMENTS_FILE,
    APT_REQUIREMENTS_FILE,
    SHELL_COMMANDS_FILE,
    PRE_BUILD_COMMANDS_FILE,
)
from cerebrium.utils.requirements import requirements_to_file, shell_commands_to_file

debug = os.environ.get("LOG_LEVEL", "INFO") == "DEBUG"


def make_cortex_dep_files(
    working_dir: str,
    config: CerebriumConfig,
):
    # Create files temporarily for upload
    requirements_files = [
        (PIP_REQUIREMENTS_FILE, config.dependencies.pip, config.dependencies.paths.get("pip")),
        (APT_REQUIREMENTS_FILE, config.dependencies.apt, config.dependencies.paths.get("apt")),
        (
            CONDA_REQUIREMENTS_FILE,
            config.dependencies.conda,
            config.dependencies.paths.get("conda"),
        ),
    ]
    for file_name, reqs, deps_file in requirements_files:
        # if deps_file and reqs then raise error
        if deps_file and reqs:
            raise ValueError(
                f"Both {file_name} and dependencies specified. Please specify only one."
            )

        # if deps_file then copy file to file_name else create file_name from reqs
        if deps_file:
            # Check if deps_file exists
            if not os.path.isfile(deps_file):
                raise FileNotFoundError(f"The specified file '{deps_file}' was not found.")

            os.system(f"cp {deps_file} {os.path.join(working_dir, file_name)}")
        if reqs:
            requirements_to_file(
                reqs,
                os.path.join(working_dir, file_name),
                is_conda=file_name == CONDA_REQUIREMENTS_FILE,
            )

    shell_commands = (SHELL_COMMANDS_FILE, config.deployment.shell_commands)
    if shell_commands[1]:
        shell_commands_to_file(
            shell_commands[1],
            os.path.join(working_dir, shell_commands[0]),
        )

    pre_build_commands = (PRE_BUILD_COMMANDS_FILE, config.deployment.pre_build_commands)
    if pre_build_commands[1]:
        shell_commands_to_file(
            pre_build_commands[1],
            os.path.join(working_dir, pre_build_commands[0]),
        )

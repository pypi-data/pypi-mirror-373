import os
import sys
import tempfile

from cerebrium.utils.logging import cerebrium_log

# Directories to exclude
EXCLUDED_DIRS = {".venv", ".conda", "__pycache__", "site-packages"}


def run_pyflakes(
    dir: str = "",
    files: list[str] = [],
    print_warnings: bool = True,
) -> tuple[list[str], list[str]]:
    try:
        import pyflakes.api
        from pyflakes.reporter import Reporter
    except ImportError:
        cerebrium_log(
            prefix="Error: Pyflakes is not installed.",
            message="To use the linting functionality, please install pyflakes by running `pip install pyflakes`.",
            level="ERROR",
        )
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp:
        warnings_log_file = os.path.join(tmp, "warnings.log")
        errors_log_file = os.path.join(tmp, "errors.log")

        with (
            open(errors_log_file, "w") as warnings_log,
            open(warnings_log_file, "w") as errors_log,
        ):
            reporter = Reporter(warningStream=warnings_log, errorStream=errors_log)

            if dir:
                # Manually walk the directory to control which folders are checked
                for root, dirs, filenames in os.walk(dir, topdown=True):
                    # Filter out excluded directories and symlinks
                    dirs[:] = [
                        d
                        for d in dirs
                        if d not in EXCLUDED_DIRS and not os.path.islink(os.path.join(root, d))
                    ]

                    # Now check each .py file
                    for filename in filenames:
                        if filename.endswith(".py"):
                            full_path = os.path.join(root, filename)
                            # Additional check if the file is a symlink
                            if not os.path.islink(full_path):
                                with open(full_path, "r") as f:
                                    code = f.read()
                                pyflakes.api.check(code, full_path, reporter=reporter)

            elif files:
                # If specific files were passed in, just check them
                for filename in files:
                    if os.path.splitext(filename)[1] != ".py":
                        continue
                    # Ensure the file isn't excluded and isn't a link
                    if any(part in EXCLUDED_DIRS for part in filename.split(os.path.sep)):
                        continue
                    if not os.path.islink(filename):
                        with open(filename, "r") as f:
                            code = f.read()
                        pyflakes.api.check(code, filename, reporter=reporter)

        with open(warnings_log_file, "r") as f:
            warnings = f.readlines()

        with open(errors_log_file, "r") as f:
            errors = f.readlines()

    filtered_errors: list[str] = []
    for e in errors:
        if "imported but unused" in e:
            warnings.append(e)
        else:
            filtered_errors.append(e)

    if warnings and print_warnings:
        warnings_to_print = "".join(warnings)
        cerebrium_log(
            prefix="Warning: Found the following warnings in your files.",
            message=f"\n{warnings_to_print}",
            level="WARNING",
        )

    if filtered_errors:
        errors_to_print = "".join(filtered_errors)
        cerebrium_log(
            prefix="Error: Found the following syntax errors in your files:",
            message=(
                f"{errors_to_print}"
                "Please fix the errors and try again. \nIf you would like to ignore these errors and deploy anyway, use the `--disable-syntax-check` flag."
            ),
            level="ERROR",
        )
    return errors, warnings

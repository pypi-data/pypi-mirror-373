import fnmatch
import os
from pathlib import Path

from cerebrium.utils.logging import cerebrium_log


def ensure_pattern_format(pattern: str):
    if not pattern:
        return pattern
    sep = os.path.sep
    if pattern.startswith(f"{sep}"):  # Starts with /
        cerebrium_log(
            prefix="ValueError",
            level="ERROR",
            message="Pattern cannot start with a forward slash. Please use a relative path.",
        )
        raise ValueError(
            "Pattern cannot start with a forward slash. Please use a relative path."
        )
    if pattern.endswith(sep):
        pattern = os.path.join(pattern, "*")
    elif os.path.isdir(pattern) and not pattern.endswith(sep):
        pattern = os.path.join(pattern, "*")

    pattern = str(Path(pattern))
    return pattern


def determine_includes(include: list[str], exclude: list[str]):
    include_set = [i.strip() for i in include]
    include_set = set(map(ensure_pattern_format, include_set))

    exclude_set = [e.strip() for e in exclude]
    exclude_set = set(map(ensure_pattern_format, exclude_set))

    file_list: list[str] = []
    for root, _, files in os.walk("."):
        for file in files:
            full_path = str(Path(root) / file)
            if any(fnmatch.fnmatch(full_path, pattern) for pattern in include_set) and not any(
                fnmatch.fnmatch(full_path, pattern) for pattern in exclude_set
            ):
                file_list.append(full_path)
    return file_list


def detect_dev_folders(file_list: list[str]) -> list[str]:
    """
    Detects development folders in the root directory of the file list.

    Args:
        file_list (list[str]): List of files to check.

    Returns:
        list[str]: List of detected development folders.
    """
    venv_folder_names = ["venv", "virtualenv", ".venv", ".git"]
    detected_folders = []

    for folder_name in venv_folder_names:
        if any(f.startswith(f"{folder_name}/") for f in file_list):
            detected_folders.append(folder_name)

    return detected_folders

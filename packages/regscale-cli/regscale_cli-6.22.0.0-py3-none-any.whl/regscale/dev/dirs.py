"""Directory paths for regscale package."""

import contextlib
import os
from pathlib import Path
from typing import Union, List
import statistics

PROFILING_DIRS = [
    "python3.8",
    "python3.9",
    "python3.10",
    "python3.11",
    "regscale-cli",
    "site-packages",
]


def get_regscale_root(file_path: str) -> str:
    """Get the root directory of the regscale directory

    :param str file_path: Path to a file in the regscale directory
    :return: Path to the root directory of the regscale directory
    :rtype: str
    """
    current_file_path = os.path.abspath(file_path)
    # start climbing the directory tree
    current_dir_path = os.path.dirname(current_file_path)
    # keep climbing until we find the regscale directory
    while True:
        last_part = os.path.basename(current_dir_path)
        if last_part == "regscale":
            # we found the regscale folder, get its parent
            root_dir = os.path.dirname(current_dir_path)
            break
        current_dir_path = os.path.dirname(current_dir_path)
    return root_dir


def trim_relative_subpath(
    path: Union[str, Path] = os.getcwd(),
    target_paths: List[Union[str, Path]] = PROFILING_DIRS,
) -> str:
    """Trim the relative subpath from the path

    :param Union[str, Path] path: The path to trim
    :param List[Union[str, Path]] target_paths: The relative subpaths to trim
    :return: The trimmed path
    :rtype: str
    """
    try:
        path = Path(path)
    except Exception:
        return str(path)
    if not path.is_absolute():
        return str(path)
    path_parts = path.parts
    last_found_index = -1
    for target_path in target_paths:
        if isinstance(target_path, str):
            target_path = Path(target_path)
        target_parts = target_path.parts
        for i, part in enumerate(path_parts):
            if part in target_parts:
                last_found_index = i
    if last_found_index == -1:
        return str(path)
    else:
        return str(Path(*path_parts[last_found_index + 1 :]))

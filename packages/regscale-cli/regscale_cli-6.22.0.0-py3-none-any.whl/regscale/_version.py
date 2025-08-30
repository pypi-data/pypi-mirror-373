"""Version information for regscale-cli."""

import re

from pathlib import Path


def get_version_from_pyproject() -> str:
    """
    Extract version from pyproject.toml

    :return: Version string if found, otherwise a fallback version
    :rtype: str
    """
    pyproject_file_name = "pyproject.toml"
    try:
        # Try multiple possible locations for pyproject.toml
        possible_paths = [
            # From the package directory
            Path(__file__).parent.parent / pyproject_file_name,
            # From current working directory
            Path.cwd() / pyproject_file_name,
            # From the project root (assuming we're in a subdirectory)
            Path.cwd().parent / pyproject_file_name,
        ]

        for pyproject_path in possible_paths:
            if pyproject_path.exists():
                content = pyproject_path.read_text()
                # Look for version = "x.y.z" pattern
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception:
        pass
    return "6.22.0.0"  # fallback version


__version__ = get_version_from_pyproject()

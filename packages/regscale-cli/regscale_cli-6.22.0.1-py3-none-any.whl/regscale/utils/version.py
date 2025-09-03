"""Version utility functions"""

import logging
import re
from functools import lru_cache

from packaging.version import Version

from regscale.core.app.utils.api_handler import APIHandler

logger = logging.getLogger(__name__)


class RegscaleVersion:
    """Utility class for managing and comparing Rescale platform versions"""

    def __init__(self):
        """Initialize RegscaleVersion with current platform version"""
        self.current_version = self.get_platform_version()

    @staticmethod
    @lru_cache(maxsize=1)
    def get_platform_version() -> str:
        """Fetch the current platform version from the API. Result is cached.

        :return: Platform version string (e.g. "1.2.3") or special version ("dev", "localdev", "Unknown")
        :rtype: str
        """
        logger.debug("Fetching platform version using API handler")
        try:
            api_handler = APIHandler()
            response = api_handler.get("/assets/json/version.json")
            if response.ok and response.status_code == 200:
                version_data = response.json()
                return version_data.get("version", "Unknown")
            else:
                logger.error(f"Failed to fetch version. Status code: {response.status_code}")
                return "Unknown"
        except Exception as e:
            logger.error(f"Error fetching version: {e}", exc_info=True)
            return "Unknown"

    @staticmethod
    def is_valid_version(version: str) -> bool:
        """Check if a version string matches semantic versioning format (X.Y.Z or X.Y.Z.W).

        :param str version: Version string to validate
        :return: True if version matches semantic versioning format
        :rtype: bool

        Examples:
            >>> RegscaleVersion.is_valid_version("1.2.3")     # Returns True
            >>> RegscaleVersion.is_valid_version("1.2.3.4")   # Returns True
            >>> RegscaleVersion.is_valid_version("1.2")       # Returns True
            >>> RegscaleVersion.is_valid_version("1.2.3.4.5") # Returns False
            >>> RegscaleVersion.is_valid_version("1.2.a")     # Returns False
        """
        return bool(re.match(r"^\d+\.\d+(\.\d+)?(\.\d+)?$", version))

    @staticmethod
    def meets_minimum_version(minimum_version: str, dev_is_latest: bool = True) -> bool:
        """Check if the given platform version meets or exceeds a minimum version requirement.

        :param str minimum_version: The minimum version required (e.g. "1.2.3")
        :param bool dev_is_latest: When True, dev is treated as newest version. When False, as oldest.
        :return: True if current platform version is new enough
        :rtype: bool

        Examples:
            >>> RegscaleVersion.meets_minimum_version("1.0.0")  # Returns True if platform version >= 1.0.0
            >>> RegscaleVersion.meets_minimum_version("2.0.0", dev_is_latest=False)  # Dev version treated as oldest
        """
        current_version = RegscaleVersion.get_platform_version()
        return RegscaleVersion.compare_versions(current_version, minimum_version, dev_is_latest)

    @staticmethod
    def compare_versions(version1: str, version2: str, dev_is_latest: bool = True) -> bool:
        """Compare two version strings.

        :param str version1: First version to compare
        :param str version2: Second version to compare
        :param bool dev_is_latest: When True, dev is treated as newest version. When False, as oldest.
        :return: True if version1 >= version2
        :rtype: bool
        """
        special_value = "9999.9999.9999.9999" if dev_is_latest else "0.0.0.0"
        special_versions = dict.fromkeys(["dev", "localdev", "Unknown"], special_value)

        # This handles if it is an epic/dev versions as they are normally in the format `BUILDNUMBER-YYYY-MM-DD`
        if "-" in version1:
            version1 = version1.split("-")[0]
        if "-" in version2:
            version2 = version2.split("-")[0]

        v1 = special_versions.get(version1, version1)
        v2 = special_versions.get(version2, version2)

        if not RegscaleVersion.is_valid_version(v2):
            logger.info(f"Invalid version {v2}, assuming dev")
            return True

        return Version(v1) >= Version(v2)

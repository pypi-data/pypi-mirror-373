"""
Container operations module for Qualys CS API integration.
"""

import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from json import JSONDecodeError
from typing import Dict, List, Optional
from urllib.parse import urljoin

from requests import RequestException
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Create logger for this module
logger = logging.getLogger("regscale")


@lru_cache(maxsize=1)
def auth_cs_api() -> tuple[str, dict]:
    """
    Authenticate the Qualys CS API using form-based authentication

    :return: A tuple of the base URL and a dictionary of headers
    :rtype: tuple[str, dict]
    """
    from . import QUALYS_API, _get_config  # noqa: C0415

    config = _get_config()
    qualys_url = config.get("qualysUrl")
    user = config.get("qualysUserName")
    password = config.get("qualysPassword")

    # Update headers to match the curl command
    auth_headers = {"X-Requested-With": "RegScale CLI"}

    # Prepare form data for authentication
    auth_data = {"username": user, "password": password, "permissions": "true", "token": "true"}

    try:
        # Make authentication request
        # https://gateway.qg3.apps.qualys.com/auth

        if qualys_url:
            base_url = qualys_url.replace("qualysguard", "gateway")
        else:
            base_url = qualys_url

        auth_url = urljoin(base_url, "/auth")
        response = QUALYS_API.post(url=auth_url, headers=auth_headers, data=auth_data)

        if response.ok:
            logger.info("Successfully authenticated with Qualys CS API")

            # Parse the response to extract the JWT token
            try:
                response_text = response.content.decode("utf-8")
                # The response should contain the JWT token
                # You might need to parse JSON or extract the token from the response
                # For now, let's assume the token is in the response text

                # Add Authorization Bearer header
                auth_headers["Authorization"] = f"Bearer {response_text}"

                logger.debug("Added Authorization Bearer header to auth_headers")
            except (UnicodeDecodeError, AttributeError) as e:
                logger.warning("Could not decode response content for Authorization header: %s", e)
                logger.debug(
                    "Response content type: %s, length: %s",
                    type(response.content),
                    len(response.content) if hasattr(response.content, "__len__") else "unknown",
                )
                # Continue without Authorization header if parsing fails
        else:
            raise RequestException(f"Authentication failed with status code: {response.status_code}")

    except Exception as e:
        logger.error("Error during authentication: %s", e)
        raise

    return base_url, auth_headers


def _make_api_request(current_url: str, headers: dict, params: Optional[Dict] = None) -> dict:
    """
    Make API request to fetch containers from Qualys CS API

    :param str current_url: The URL for the API request
    :param dict headers: Headers to include in the request
    :param Dict params: Optional query parameters for pagination
    :return: Response data containing containers and response object
    :rtype: dict
    """
    from . import QUALYS_API  # noqa: C0415

    # Make API request
    response = QUALYS_API.get(url=current_url, headers=headers, params=params)

    # Validate response
    if not response.ok:
        logger.error("API request failed: %s - %s", response.status_code, response.text)
        return {"data": [], "_response": response}

    try:
        response_data = response.json()
        response_data["_response"] = response  # Include response object for headers
        return response_data
    except JSONDecodeError as e:
        logger.error("Failed to parse JSON response: %s", e)
        return {"data": [], "_response": response}


def _parse_link_header(link_header: str) -> Optional[str]:
    """
    Parse the Link header to find the next page URL.

    :param str link_header: The Link header value
    :return: The next page URL or None if not found
    :rtype: Optional[str]
    """
    if not link_header:
        logger.debug("No Link header found, assuming no more pages")
        return None

    # Parse the Link header to find the next page URL
    # Format: <url>;rel=next
    for link in link_header.split(","):
        link = link.strip()
        if "rel=next" in link:
            # Extract URL from <url>;rel=next format
            url_start = link.find("<") + 1
            url_end = link.find(">")
            if 0 < url_start < url_end:
                return link[url_start:url_end]

    logger.debug("No next page URL found in Link header")
    return None


def _fetch_paginated_data(endpoint: str, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Generic function to fetch paginated data from Qualys CS API

    :param str endpoint: The API endpoint (e.g., 'containers/list', 'images/list')
    :param Optional[Dict] filters: Filters to apply to the request
    :param int limit: Number of items to fetch per page
    :return: A list of items from all pages
    :rtype: List[Dict]
    """
    all_items = []
    page: int = 1
    current_url = None  # Ensure current_url is always defined

    try:
        # Get authentication
        base_url, headers = auth_cs_api()

        # Prepare base parameters
        params = {"limit": limit}

        # Add filters if provided
        if filters:
            params.update(filters)

        # Track the current URL for pagination
        current_url = urljoin(base_url, f"/csapi/v1.3/{endpoint}")

        # Create progress bar for pagination
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=None,
        )

        with progress:
            task = progress.add_task(f"[green]Fetching {endpoint} data...", total=None)  # Unknown total for pagination

            while current_url:
                # Make API request
                response_data = _make_api_request(current_url, headers, params)

                # Extract items from current page
                current_items = response_data.get("data", [])
                all_items.extend(current_items)

                # Update progress description with current status
                progress.update(
                    task, description=f"[green]Fetching {endpoint} data... (Page {page}, Total: {len(all_items)})"
                )

                logger.debug("Fetched page: %s items (Total so far: %s)", page, len(all_items))

                # Check for next page using the Link header
                response = response_data.get("_response")
                if not response or not hasattr(response, "headers"):
                    # If no response object available, assume single page
                    break

                link_header = response.headers.get("link", "")
                next_url = _parse_link_header(link_header)

                if not next_url:
                    break

                # Update current URL for next iteration
                current_url = next_url
                page += 1

                # Clear params for subsequent requests since they're in the URL
                params = {}
            progress.update(task, total=len(all_items))
            progress.update(task, completed=len(all_items))

    except Exception as e:
        logger.error("Error fetching data from %s: %s", current_url if current_url else "N/A", e)
        logger.debug(traceback.format_exc())

    logger.info("Completed: Fetched %s total items from %s", len(all_items), endpoint)
    return all_items


def fetch_all_containers(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Fetch all containers from Qualys CS API with pagination

    :param Optional[Dict] filters: Filters to apply to the containers
    :param int limit: Number of containers to fetch per page
    :return: A list of containers
    :rtype: List[Dict]
    """
    return _fetch_paginated_data("containers/list", filters, limit)


def fetch_all_images(filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
    """
    Fetch all images from Qualys CS API with pagination

    :param Optional[Dict] filters: Filters to apply to the images
    :param int limit: Number of images to fetch per page
    :return: A list of images
    :rtype: List[Dict]
    """
    return _fetch_paginated_data("images/list", filters, limit)


def fetch_container_vulns(container_sha: str) -> List[Dict]:
    """
    Fetch vulnerabilities for a specific container from Qualys CS API

    :param str container_sha: The SHA of the container
    :return: A list of vulnerabilities
    :rtype: List[Dict]
    """
    base_url, headers = auth_cs_api()
    current_url = urljoin(base_url, f"/csapi/v1.3/containers/{container_sha}/vuln")
    response_data = _make_api_request(current_url, headers)
    return response_data.get("details", {}).get("vulns", [])


def fetch_all_vulnerabilities(filters: Optional[Dict] = None, limit: int = 100, max_workers: int = 10) -> List[Dict]:
    """
    Fetch all containers and a list of vulnerabilities for each container from Qualys CS API with pagination

    :param Optional[Dict] filters: Filters to apply to the containers
    :param int limit: Number of containers to fetch per page
    :param int max_workers: Maximum number of worker threads for concurrent vulnerability fetching
    :return: A list of containers with vulnerabilities
    :rtype: List[Dict]
    """
    containers = fetch_all_containers(filters, limit)

    if not containers:
        logger.info("No containers found to fetch vulnerabilities for")
        return containers

    # Create progress bar for fetching vulnerabilities
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=None,
    )

    def fetch_container_vulns_with_progress(container):
        """Helper function to fetch vulnerabilities for a single container with progress tracking."""
        container_sha = container.get("sha")
        if not container_sha:
            logger.warning("Container missing SHA, skipping vulnerability fetch")
            return container, []

        try:
            vulns = fetch_container_vulns(container_sha)
            logger.debug("Fetched %s vulnerabilities for container %s...", len(vulns), container_sha[:8])
            return container, vulns
        except Exception as e:
            logger.error("Error fetching vulnerabilities for container %s: %s", container_sha, e)
            return container, []

    with progress:
        task = progress.add_task(
            f"[yellow]Fetching vulnerabilities for {len(containers)} containers...", total=len(containers)
        )

        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_container = {}
            for container in containers:
                future = executor.submit(fetch_container_vulns_with_progress, container)
                future_to_container[future] = container

            # Process completed tasks and update progress
            for future in as_completed(future_to_container):
                container, vulns = future.result()
                container["vulnerabilities"] = vulns
                progress.update(task, advance=1)

    logger.info("Completed fetching vulnerabilities for %s containers using %s workers", len(containers), max_workers)
    return containers

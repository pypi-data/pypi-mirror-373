#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data fetching and caching logic for Wiz Policy Compliance."""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from regscale.integrations.commercial.wizv2.async_client import run_async_queries
from regscale.integrations.commercial.wizv2.constants import WizVulnerabilityType, WIZ_POLICY_QUERY

logger = logging.getLogger("regscale")


class WizDataCache:
    """Manages caching of Wiz API responses."""

    def __init__(self, cache_dir: str, cache_duration_minutes: int = 0) -> None:
        """
        Initialize the Wiz data cache.

        :param cache_dir: Directory to store cache files
        :param cache_duration_minutes: Cache TTL in minutes (0 = disabled)
        """
        self.cache_dir = cache_dir
        self.cache_duration_minutes = cache_duration_minutes
        self.force_refresh = False

    def get_cache_file_path(self, wiz_project_id: str, framework_id: str) -> str:
        """
        Get cache file path for given project and framework.

        :param wiz_project_id: Wiz project ID
        :param framework_id: Framework ID
        :return: Full path to cache file
        """
        os.makedirs(self.cache_dir, exist_ok=True)
        return os.path.join(self.cache_dir, f"policy_assessments_{wiz_project_id}_{framework_id}.json")

    def is_cache_valid(self, cache_file: str) -> bool:
        """
        Check if cache file exists and is within TTL.

        :param cache_file: Path to cache file to check
        :return: True if cache is valid, False otherwise
        """
        if self.force_refresh or self.cache_duration_minutes <= 0:
            return False

        if not os.path.exists(cache_file):
            return False

        try:
            max_age_seconds = self.cache_duration_minutes * 60
            file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
            return file_age <= max_age_seconds
        except Exception:
            return False

    def load_from_cache(self, cache_file: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load data from cache file.

        :param cache_file: Path to cache file to load
        :return: Cached assessment nodes if valid, None otherwise
        """
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            nodes = data.get("nodes") or data.get("assessments") or []
            return nodes if isinstance(nodes, list) else None
        except Exception as e:
            logger.debug(f"Error loading cache: {e}")
            return None

    def save_to_cache(
        self, cache_file: str, nodes: List[Dict[str, Any]], wiz_project_id: str, framework_id: str
    ) -> None:
        """
        Save data to cache file.

        :param cache_file: Path to cache file
        :param nodes: Assessment nodes to cache
        :param wiz_project_id: Wiz project ID for metadata
        :param framework_id: Framework ID for metadata
        """
        if self.cache_duration_minutes <= 0:
            return

        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "wiz_project_id": wiz_project_id,
                "framework_id": framework_id,
                "nodes": nodes,
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Error writing cache: {e}")


class WizApiClient:
    """Handles Wiz API interactions."""

    def __init__(self, endpoint: str, access_token: str) -> None:
        """
        Initialize the Wiz API client.

        :param endpoint: Wiz GraphQL API endpoint URL
        :param access_token: Wiz API access token
        """
        self.endpoint = endpoint
        self.access_token = access_token

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.

        :return: Dictionary of HTTP headers including authorization
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def fetch_policy_assessments_async(
        self, wiz_project_id: str, progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch policy assessments using async client.

        :param wiz_project_id: Wiz project ID
        :param progress_callback: Optional progress callback
        :return: List of policy assessment nodes
        """
        try:
            page_size = 100
            query_config = {
                "type": WizVulnerabilityType.CONFIGURATION,
                "query": WIZ_POLICY_QUERY,
                "topic_key": "policyAssessments",
                "variables": {"first": page_size},
            }

            # Import here to avoid circular imports during testing
            from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

            with compliance_job_progress:
                task = compliance_job_progress.add_task(
                    f"[#f68d1f]Fetching Wiz policy assessments (async, page size: {page_size})...",
                    total=1,
                )

                results = run_async_queries(
                    endpoint=self.endpoint,
                    headers=self.get_headers(),
                    query_configs=[query_config],
                    progress_tracker=compliance_job_progress,
                    max_concurrent=1,
                )

                compliance_job_progress.update(task, completed=1, advance=1)

            if results and len(results) == 1 and not results[0][2]:
                return results[0][1] or []

            return []
        except Exception as e:
            logger.debug(f"Async fetch failed: {e}")
            raise

    def fetch_policy_assessments_requests(
        self,
        base_variables: Dict[str, Any],
        filter_variants: List[Optional[Dict[str, Any]]],
        progress_callback: Optional[Callable] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch policy assessments using requests library with filter variants.

        :param base_variables: Base GraphQL variables
        :param filter_variants: List of filter variants to try
        :param progress_callback: Optional progress callback
        :return: List of policy assessment nodes
        """

        session = self._create_requests_session()
        last_error = None

        for filter_variant in filter_variants:
            try:
                variables = base_variables.copy()
                if filter_variant is not None:
                    variables["filterBy"] = filter_variant

                nodes = self._execute_paginated_query(session, variables, progress_callback)
                return nodes
            except Exception as e:
                last_error = e
                logger.debug(f"Filter variant {filter_variant} failed: {e}")
                continue

        raise Exception(f"All filter variants failed. Last error: {last_error}")

    def _create_requests_session(self):
        """
        Create requests session with retry logic.

        :return: Configured requests session with retry adapter
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    def _execute_paginated_query(
        self, session, variables: Dict[str, Any], progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute paginated GraphQL query.

        :param session: Requests session object
        :param variables: GraphQL query variables
        :param progress_callback: Optional callback for progress updates
        :return: List of assessment nodes from all pages
        """
        import requests

        nodes = []
        after_cursor = variables.get("after")
        page_index = 0

        while True:
            payload_vars = variables.copy()
            payload_vars["after"] = after_cursor
            payload = {"query": WIZ_POLICY_QUERY, "variables": payload_vars}

            response = session.post(self.endpoint, json=payload, headers=self.get_headers(), timeout=300)

            if response.status_code >= 400:
                raise requests.HTTPError(f"{response.status_code} {response.text[:500]}")

            data = response.json()
            if "errors" in data:
                raise RuntimeError(str(data["errors"]))

            topic = data.get("data", {}).get("policyAssessments", {})
            page_nodes = topic.get("nodes", [])
            page_info = topic.get("pageInfo", {})

            nodes.extend(page_nodes)
            page_index += 1

            if progress_callback:
                try:
                    progress_callback(page_index, len(page_nodes), len(nodes))
                except Exception:
                    pass

            has_next = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

            if not has_next:
                break

        return nodes


class PolicyAssessmentFetcher:
    """Main class for fetching Wiz policy assessments."""

    def __init__(
        self,
        wiz_endpoint: str,
        access_token: str,
        wiz_project_id: str,
        framework_id: str,
        cache_duration_minutes: int = 0,
    ) -> None:
        """
        Initialize the policy assessment fetcher.

        :param wiz_endpoint: Wiz GraphQL API endpoint URL
        :param access_token: Wiz API access token
        :param wiz_project_id: Wiz project ID to query
        :param framework_id: Framework ID to filter by
        :param cache_duration_minutes: Cache TTL in minutes (0 = disabled)
        """
        self.api_client = WizApiClient(wiz_endpoint, access_token)
        self.wiz_project_id = wiz_project_id
        self.framework_id = framework_id
        self.cache = WizDataCache("artifacts/wiz", cache_duration_minutes)

    def fetch_policy_assessments(self) -> List[Dict[str, Any]]:
        """
        Fetch policy assessments from Wiz API with caching.

        :return: List of filtered policy assessment nodes
        """
        logger.info("Fetching policy assessments from Wiz...")

        # Try cache first
        cache_file = self.cache.get_cache_file_path(self.wiz_project_id, self.framework_id)

        if self.cache.is_cache_valid(cache_file):
            cached_nodes = self.cache.load_from_cache(cache_file)
            if cached_nodes is not None:
                logger.info("Using cached Wiz policy assessments")
                return cached_nodes

        # Fetch from API
        try:
            # Try async client first
            nodes = self._fetch_with_async_client()
        except Exception:
            # Fall back to requests
            logger.debug("Async client failed, falling back to requests")
            nodes = self._fetch_with_requests()

        # Filter to framework
        filtered_nodes = self._filter_nodes_to_framework(nodes)

        # Save to cache
        self.cache.save_to_cache(cache_file, filtered_nodes, self.wiz_project_id, self.framework_id)

        return filtered_nodes

    def _fetch_with_async_client(self) -> List[Dict[str, Any]]:
        """
        Fetch using async client.

        :return: List of policy assessment nodes
        """
        return self.api_client.fetch_policy_assessments_async(self.wiz_project_id)

    def _fetch_with_requests(self) -> List[Dict[str, Any]]:
        """
        Fetch using requests with filter variants.

        :return: List of policy assessment nodes
        """
        page_size = 100
        base_variables = {"first": page_size}

        # Try multiple filter variants
        filter_variants = [
            {"project": [self.wiz_project_id]},
            {"projectId": [self.wiz_project_id]},
            {"projects": [self.wiz_project_id]},
            {},  # Empty filterBy
            None,  # Omit filterBy entirely
        ]

        return self.api_client.fetch_policy_assessments_requests(base_variables, filter_variants)

    def _filter_nodes_to_framework(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter nodes to only include items from the target framework.

        :param nodes: Raw assessment nodes from Wiz API
        :return: Filtered nodes belonging to the target framework
        """
        filtered_nodes = []

        for node in nodes:
            try:
                subcats = ((node or {}).get("policy") or {}).get("securitySubCategories", [])

                # Include if no subcategories (can't evaluate framework)
                if not subcats:
                    filtered_nodes.append(node)
                    continue

                # Include if any subcategory matches our framework
                for subcat in subcats:
                    framework_id = subcat.get("category", {}).get("framework", {}).get("id")
                    if framework_id == self.framework_id:
                        filtered_nodes.append(node)
                        break

            except Exception:
                # Include on error (defensive)
                filtered_nodes.append(node)

        return filtered_nodes

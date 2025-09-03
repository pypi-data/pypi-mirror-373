#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Async GraphQL client for Wiz integration with concurrent query processing."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

import anyio
import httpx

from regscale.core.app.utils.app_utils import error_and_exit
from regscale.integrations.variables import ScannerVariables

logger = logging.getLogger("regscale")


class AsyncWizGraphQLClient:
    """
    Async GraphQL client optimized for concurrent Wiz API queries.

    This client can execute multiple GraphQL queries concurrently, significantly
    improving performance when fetching different finding types from Wiz.
    """

    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_concurrent: int = 5,
    ):
        """
        Initialize the async GraphQL client.

        :param str endpoint: GraphQL endpoint URL
        :param Optional[Dict[str, str]] headers: HTTP headers for requests
        :param float timeout: Request timeout in seconds
        :param int max_concurrent: Maximum concurrent requests
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self._semaphore = anyio.Semaphore(max_concurrent)

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None,
        task_name: str = "GraphQL Query",
    ) -> Dict[str, Any]:
        """
        Execute a single GraphQL query asynchronously.

        :param str query: GraphQL query string
        :param Optional[Dict[str, Any]] variables: Query variables
        :param Optional[callable] progress_callback: Callback for progress updates
        :param str task_name: Name for progress tracking
        :return: Query response data
        :rtype: Dict[str, Any]
        """
        async with self._semaphore:  # Limit concurrent requests
            if progress_callback:
                progress_callback(task_name, "starting")

            payload = {"query": query, "variables": variables or {}}

            # Debug logging for authentication and payload
            logger.debug(f"Async GraphQL request to {self.endpoint}")
            logger.debug(f"Headers: {self.headers}")
            logger.debug(f"Variables: {variables}")

            try:
                # Get SSL verify setting from scanner variables config
                ssl_verify = getattr(ScannerVariables, "sslVerify", True)
                async with httpx.AsyncClient(timeout=self.timeout, verify=ssl_verify) as client:
                    if progress_callback:
                        progress_callback(task_name, "requesting")

                    response = await client.post(self.endpoint, json=payload, headers=self.headers)

                    if progress_callback:
                        progress_callback(task_name, "processing")

                    if not response.is_success:
                        error_and_exit(
                            f"Received non-200 response from GraphQL API: {response.status_code}: {response.text}"
                        )
                    result = response.json()

                    if "errors" in result:
                        error_msg = f"GraphQL errors: {result['errors']}"
                        logger.error(error_msg)
                        error_and_exit(error_msg)

                    if progress_callback:
                        progress_callback(task_name, "completed")

                    return result.get("data", {})

            except httpx.HTTPError as e:
                error_msg = f"HTTP error in {task_name}: {str(e)}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(task_name, "failed")
                error_and_exit(error_msg)
            except Exception as e:
                error_msg = f"Error in {task_name}: {str(e)}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(task_name, "failed")
                error_and_exit(error_msg)

    async def execute_paginated_query(
        self,
        query: str,
        variables: Dict[str, Any],
        topic_key: str,
        progress_callback: Optional[callable] = None,
        task_name: str = "Paginated Query",
    ) -> List[Dict[str, Any]]:
        """
        Execute a paginated GraphQL query, fetching all pages.

        :param str query: GraphQL query string
        :param Dict[str, Any] variables: Query variables
        :param str topic_key: Key to extract nodes from response
        :param Optional[callable] progress_callback: Callback for progress updates
        :param str task_name: Name for progress tracking
        :return: All nodes from all pages
        :rtype: List[Dict[str, Any]]
        """
        all_nodes = []
        has_next_page = True
        after_cursor = None
        page_count = 0

        while has_next_page:
            page_count += 1
            current_variables = variables.copy()
            current_variables["after"] = after_cursor

            page_task_name = f"{task_name} (Page {page_count})"

            try:
                data = await self.execute_query(
                    query=query,
                    variables=current_variables,
                    progress_callback=progress_callback,
                    task_name=page_task_name,
                )

                topic_data = data.get(topic_key, {})
                nodes = topic_data.get("nodes", [])
                page_info = topic_data.get("pageInfo", {})

                # Handle case where nodes is explicitly None
                if nodes is None:
                    nodes = []

                all_nodes.extend(nodes)

                has_next_page = page_info.get("hasNextPage", False)
                after_cursor = page_info.get("endCursor")

                if progress_callback:
                    progress_callback(
                        task_name,
                        f"fetched_page_{page_count}",
                        {"nodes_count": len(nodes), "total_nodes": len(all_nodes)},
                    )

            except Exception as e:
                logger.error(f"Error fetching page {page_count} for {task_name}: {str(e)}")
                break

        return all_nodes

    def _create_progress_callback(self, progress_tracker: Any, task_id: Any, query_type: str) -> callable:
        """
        Create a progress callback function for query execution tracking.

        :param Any progress_tracker: Progress tracker instance
        :param Any task_id: Task ID for progress updates
        :param str query_type: Type of query being executed
        :return: Progress callback function
        :rtype: callable
        """

        def progress_callback(task_name: str, status: str, extra_data: Dict = None):
            status_messages = {
                "starting": f"[yellow]Starting {query_type}...",
                "requesting": f"[blue]Querying {query_type}...",
                "processing": f"[magenta]Processing {query_type}...",
                "completed": f"[green]✓ Completed {query_type}",
                "failed": f"[red]✗ Failed {query_type}",
            }

            if status in status_messages:
                progress_tracker.update(task_id, description=status_messages[status])
            elif status.startswith("fetched_page_") and extra_data:
                progress_tracker.update(
                    task_id, description=f"[cyan]{query_type}: {extra_data['total_nodes']} nodes fetched"
                )

        return progress_callback

    async def _execute_single_query_config(
        self, config: Dict[str, Any], progress_tracker: Optional[Any] = None
    ) -> Tuple[str, List[Dict[str, Any]], Optional[Exception]]:
        """
        Execute a single query configuration with progress tracking.

        :param Dict[str, Any] config: Query configuration
        :param Optional[Any] progress_tracker: Progress tracker for UI updates
        :return: Tuple of (query_type, results, error)
        :rtype: Tuple[str, List[Dict[str, Any]], Optional[Exception]]
        """
        query_type = config["type"].value
        query = config["query"]
        variables = config.get("variables", {})
        topic_key = config["topic_key"]

        # Setup progress tracking if available
        progress_callback = None
        task_id = None

        if progress_tracker:
            task_id = progress_tracker.add_task(f"[yellow]Fetching {query_type}...", total=None)
            progress_callback = self._create_progress_callback(progress_tracker, task_id, query_type)

        try:
            # Execute paginated query
            nodes = await self.execute_paginated_query(
                query=query,
                variables=variables,
                topic_key=topic_key,
                progress_callback=progress_callback,
                task_name=query_type,
            )

            # Update progress on success
            if task_id and progress_tracker:
                progress_tracker.update(
                    task_id, description=f"[green]✓ {query_type}: {len(nodes)} nodes", completed=1, total=1
                )

            return query_type, nodes, None

        except Exception as e:
            # Update progress on failure
            if task_id and progress_tracker:
                progress_tracker.update(
                    task_id, description=f"[red]✗ {query_type}: {str(e)[:50]}...", completed=1, total=1
                )
            return query_type, [], e

    def _process_concurrent_results(
        self, results: List[Any], query_configs: List[Dict[str, Any]]
    ) -> List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]:
        """
        Process results from concurrent query execution.

        :param List[Any] results: Raw results from asyncio.gather
        :param List[Dict[str, Any]] query_configs: Original query configurations
        :return: Processed results
        :rtype: List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]
        """
        processed_results = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                query_type = query_configs[i]["type"].value
                processed_results.append((query_type, [], result))
            else:
                processed_results.append(result)

        return processed_results

    async def execute_concurrent_queries(
        self, query_configs: List[Dict[str, Any]], progress_tracker: Optional[Any] = None
    ) -> List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]:
        """
        Execute multiple GraphQL queries concurrently.

        :param List[Dict[str, Any]] query_configs: List of query configurations
        :param Optional[Any] progress_tracker: Progress tracker for UI updates
        :return: List of (query_type, results, error) tuples
        :rtype: List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]
        """
        logger.info(f"Starting {len(query_configs)} concurrent GraphQL queries...")

        # Create tasks for concurrent execution
        tasks = [self._execute_single_query_config(config, progress_tracker) for config in query_configs]

        # Execute all queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process and return results
        processed_results = self._process_concurrent_results(results, query_configs)

        logger.info(f"Completed {len(query_configs)} concurrent queries")
        return processed_results


def run_async_queries(
    endpoint: str,
    headers: Dict[str, str],
    query_configs: List[Dict[str, Any]],
    progress_tracker: Optional[Any] = None,
    max_concurrent: int = 5,
    timeout: int = 60,
) -> List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]:
    """
    Convenience function to run async queries from synchronous code.

    :param str endpoint: GraphQL endpoint URL
    :param Dict[str, str] headers: HTTP headers
    :param List[Dict[str, Any]] query_configs: Query configurations
    :param Optional[Any] progress_tracker: Progress tracker
    :param int max_concurrent: Maximum concurrent requests
    :param int timeout: Request timeout in seconds
    :return: Query results
    :rtype: List[Tuple[str, List[Dict[str, Any]], Optional[Exception]]]
    """

    async def _run():
        client = AsyncWizGraphQLClient(
            endpoint=endpoint, headers=headers, max_concurrent=max_concurrent, timeout=timeout
        )
        return await client.execute_concurrent_queries(query_configs, progress_tracker)

    # Use anyio.run for better compatibility
    return anyio.run(_run)

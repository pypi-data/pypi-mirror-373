import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from regscale.core.app.utils.app_utils import error_and_exit, check_file_path
from regscale.integrations.commercial.wizv2.constants import CONTENT_TYPE
from regscale.core.app.application import Application
from regscale.utils import PaginatedGraphQLClient

logger = logging.getLogger("regscale")


class WizMixin(Application):
    def fetch_data_if_needed(
        self,
        file_path: str,
        query: str,
        topic_key: str,
        interval_hours: int,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        """
        Fetches data if the file is not present or is older than the fetch interval
        :param str file_path: File path to write to
        :param str query: GraphQL Query
        :param str topic_key: Topic Key
        :param int interval_hours: Interval in hours to fetch new data
        :param Optional[Dict[str, Any]] variables: Variables
        :returns: List[Dict] of data nodes
        :rtype: List[Dict]
        """
        fetch_interval = timedelta(hours=interval_hours)  # Interval to fetch new data
        current_time = datetime.now()

        # Check if the file exists and its last modified time
        if os.path.exists(file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if current_time - file_mod_time < fetch_interval:
                nodes = self.load_file(file_path)
                return nodes
        nodes = self.fetch_data(query, topic_key, variables)
        self.write_to_file(file_path, nodes)
        return nodes

    @staticmethod
    def write_to_file(file_path: str, nodes: List[Dict]):
        """
        Writes the nodes to a file
        :param str file_path: File path to write to
        :param List[Dict] nodes: List of nodes to write
        """
        check_file_path("artifacts")
        with open(file_path, "w") as file:
            json.dump(nodes, file)

    @staticmethod
    def load_file(file_path: str) -> List[Dict]:
        """
        Loads the file and maps the nodes to Vulnerability objects
        :param str file_path: File path to load
        Returns: List of Dict
        :rtype: List[Dict]
        """
        check_file_path("artifacts")
        with open(file_path, "r") as file:
            return json.load(file)

    def fetch_data(self, query: str, topic_key: str, variables: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Fetches data from Wiz
        :param str query: GraphQL Query
        :param str topic_key: Topic Key
        :param Optional[Dict[str, Any]] variables: Variables
        :returns: List of nodes
        :rtype: List[Dict]
        """
        client = None
        api_endpoint_url = self.config.get("wizUrl")
        if not api_endpoint_url:
            logger.error("Wiz API endpoint not configured")
            error_and_exit("Wiz API endpoint not configured")
        if token := self.config.get("wizAccessToken"):
            client = PaginatedGraphQLClient(
                endpoint=api_endpoint_url,
                query=query,
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Authorization": "Bearer " + token,
                },
            )

        logger.info(f"Fetching data from Wiz on topic key for {topic_key}")
        # Fetch all results using the client's pagination logic
        data = client.fetch_all(variables=variables, topic_key=topic_key) if client else []
        return data

import json
import logging
import sys
from typing import List, Dict, Optional

from regscale.core.app.utils.app_utils import error_and_exit
from regscale.integrations.commercial.wizv2.WizDataMixin import WizMixin
from regscale.models.regscale_models.sbom import Sbom
from regscale.integrations.commercial.wizv2.constants import SBOM_QUERY, SBOM_FILE_PATH
from regscale.utils import get_value

logger = logging.getLogger(__name__)


class WizSbomIntegration(WizMixin):
    """
    Integration class for handling SBOM data from Wiz.io

    :param Optional[str] wiz_project_id: The Wiz project ID
    :param int regscale_id: The RegScale ID
    :param str regscale_module: The RegScale module
    :param Optional[str] filter_by_override: The filterBy override
    :param str client_id: The client ID
    :param str client_secret: The client secret
    """

    def __init__(
        self,
        wiz_project_id: Optional[str],
        regscale_id: int,
        regscale_module: str,
        filter_by_override: Optional[str],
        client_id: str,
        client_secret: str,
    ):
        super().__init__()
        self.sbom_list: List[Sbom] = []
        self.wiz_project_id = wiz_project_id or self.config.get("wizProjectId")
        if not self.wiz_project_id:
            error_and_exit("Wiz project ID not provided")
        self.regscale_id = regscale_id
        self.regscale_module = regscale_module
        self.filter_by_override: Optional[str] = filter_by_override
        self.client_id = client_id
        self.client_secret = client_secret
        self.filter_by = json.loads(filter_by_override) if filter_by_override else None
        self.topic_key = "sbomArtifactsGroupedByName"
        self.variables = {
            "first": 200,
            "filterBy": {"project": str(self.wiz_project_id)},
            "orderBy": {"field": "NAME", "direction": "ASC"},
        }
        if self.filter_by:
            logger.info(f"Using filterBy override: {self.filter_by}")
            self.variables = {
                "first": 200,
                "filterBy": self.filter_by,
                "orderBy": {"field": "NAME", "direction": "ASC"},
            }

    def run(self):
        """
        Run the integration process
        """
        self.fetch_sbom_data()
        if not self.sbom_list:
            logger.info("No SBOM data found")
            sys.exit(0)
        existing_sboms: List[Sbom] = Sbom.get_all_by_parent(
            parent_id=self.regscale_id, parent_module=self.regscale_module
        )
        existing_sbom_names = [sbom.name for sbom in existing_sboms]
        for sbom in self.sbom_list:
            if sbom.name not in existing_sbom_names:
                sbom.create()
                logger.info(f"Successfully created SBOM {sbom.name}")
            else:
                logger.info(f"SBOM {sbom.name} already exists in RegScale")

    def fetch_sbom_data(self):
        """
        Fetch SBOM data from Wiz.io using the SBOM_QUERY
        """
        logger.info("Fetching SBOM data from Wiz")
        logger.info(f"Fetching SBOM data for project ID: {self.wiz_project_id}")
        logger.info(f"Fetching SBOM data for topic_key: {self.topic_key}")
        logger.info(f"Fetching SBOM data for variables: {self.variables}")
        interval_hours = self.config.get("wizFullPullLimitHours", 8)
        nodes = self.fetch_data_if_needed(
            file_path=SBOM_FILE_PATH,
            query=SBOM_QUERY,
            topic_key=self.topic_key,
            interval_hours=interval_hours,
            variables=self.variables,
        )
        logger.info(f"Fetched {len(nodes)} SBOM data from Wiz")
        self.map_sbom_data(nodes)

    def map_sbom_data(self, nodes: List[Dict]):
        """
        Map the fetched SBOM data to the Sbom model
        :nodes List[Dict] sbom_data: List of SBOM data
        """
        for data in nodes:
            versions = [version_dict.get("version") for version_dict in get_value(data, "versions.nodes")]
            sbom = Sbom(
                name=data.get("name"),
                sbomStandard=get_value(data, "type.codeLibraryLanguage") or data.get("name"),
                standardVersion=",".join(versions) if versions else "",
                tool=get_value(data, "type.group"),
                parentId=self.regscale_id,
                parentModule=self.regscale_module,
                results=json.dumps(data),
            )
            self.sbom_list.append(sbom)

from typing import List, Optional
from typing_extensions import TypedDict

from lxml import etree
from pydantic import BaseModel, ConfigDict, Field

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.reporting import log_error, log_event
from regscale.models import regscale_models, StakeHolder, SystemRole

logger = create_logger()


class LogEventArgs(TypedDict):
    """
    Args for the log_event function.
    """

    record_type: str
    event_msg: str
    model_layer: str


class LogErrorArgs(TypedDict):
    """
    Args for the log_error function.
    """

    record_type: str
    missing_element: Optional[str]
    model_layer: str
    event_msg: str


class FedrampTraversalError(TypedDict):
    timestamp: str
    level: str
    model_layer: str
    record_type: str
    event: str


class FedrampTraversalInfo(TypedDict):
    timestamp: str
    level: str
    model_layer: str
    record_type: str
    event: str


class FedrampTraversal(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # The Regscale API object we'll use to post from this traversal.
    api: Api

    # The root XML element.
    root: etree._Element

    # Namespaces for this traversal
    namespaces: Optional[dict] = None

    # This is the id of the ssp in RegScale, if it has been created.
    ssp_id: Optional[int] = None

    # This is the id of the catalogue in RegScale that the user has selected during upload.
    catalogue_id: Optional[int] = None

    # List of errors that have occurred during the traversal.
    errors: List[FedrampTraversalError] = Field(default_factory=list)

    # List of info messages that have occurred during the traversal.
    infos: List[FedrampTraversalInfo] = Field(default_factory=list)

    def fedramp_role_id_to_regscale_system_role_id(self, fedramp_role_id: str) -> Optional[int]:
        """
        Get the RegScale SystemRole.id for a FedRAMP role id, contained in this SSP.

        If no such mapping exists, returns None.
        """
        # FUTURE-TODO: SPEED-OPTIMIZATION -- This could be cached on the traversal object,
        # so it doesn't have to be refetched.
        ssp_system_roles = SystemRole.get_all_by_ssp_id(self.api.app, self.ssp_id)

        try:
            matching_system_roles = [
                system_role for system_role in ssp_system_roles if system_role["fedrampRoleId"] == fedramp_role_id
            ]
        except (KeyError, AttributeError):
            matching_system_roles = [
                system_role for system_role in ssp_system_roles if system_role.fedrampRoleId == fedramp_role_id
            ]

        first_matching_system_role = matching_system_roles[0] if matching_system_roles else None
        return first_matching_system_role["id"] if first_matching_system_role else None

    def fedramp_party_to_regscale_stakeholder_id(self, party_fedramp_uuid: str) -> Optional[int]:
        """
        Get the RegScale Stakeholder.id for a FedRAMP party UUID, contained in this SSP.

        If no such mapping exists, returns None.
        """
        # Parties MIGHT be able to be multiple things
        # FOR SURE
        # - Stakeholder
        # All stakeholders
        # FUTURE-TODO: SPEED-OPTIMIZATION -- This could be cached on the traversal object,
        # so it doesn't have to be refetched.
        stakeholders = StakeHolder.get_all_by_parent(
            parent_id=self.ssp_id,
            parent_module=regscale_models.SecurityPlan.get_module_slug(),
        )

        # Debug only.
        logger.debug("stakeholders", stakeholders)

        # get stakeholders with otherID = party_fedramp_uuid
        matching_stakeholders = [
            stakeholder for stakeholder in stakeholders if stakeholder.otherID == party_fedramp_uuid
        ]

        first_matching_stakeholder = matching_stakeholders[0] if matching_stakeholders else None

        return first_matching_stakeholder.id if first_matching_stakeholder else None

        # TODO-FUTURE: MAYBE these need to be handled too?
        # - SystemRole
        # - User (probably not)

    # Add an error to the traversal.
    def log_error(self, error: LogErrorArgs):
        # logger.error(f"{error.error_level}: {error.error_msg}")
        self.errors.append(log_error(**error, level="Error"))

    def log_info(self, event: LogEventArgs):
        # logger.info(f"{info.info_level}: {info.info_msg}")
        self.infos.append(log_event(**event, level="Info"))

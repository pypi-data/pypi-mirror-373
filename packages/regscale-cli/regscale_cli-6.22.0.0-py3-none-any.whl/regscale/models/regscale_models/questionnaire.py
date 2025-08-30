# pylint: disable=C0301
"""
This module contains the Questionnaires model in RegScale.
"""

import logging
from typing import List, Optional

from pydantic import ConfigDict

from regscale.models.regscale_models.questionnaire_instance import QuestionnaireInstance
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger(__name__)


class Questionnaires(RegScaleModel):
    """
    A class to represent the Questionnaires model in RegScale.
    """

    _module_slug = "questionnaires"
    _unique_fields = [["title", "parentQuestionnaireId"]]

    id: Optional[int] = 0
    uuid: Optional[str] = None
    title: str
    ownerId: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    tenantsId: Optional[int] = 1
    active: bool = True
    isPublic: bool = True
    sections: Optional[List[int]] = [0]  # Adjust the type if it's not a string
    rules: Optional[str] = None  # Adjust the type if it's not a string
    loginRequired: Optional[bool] = True
    allowPublicUrl: Optional[bool] = True
    enableScoring: Optional[bool] = False
    questionnaireIds: Optional[List[int]] = None
    parentQuestionnaireId: Optional[int] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get endpoints for the Questionnaire model.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/getCount",
            graph_post="/api/{model_slug}/graph",
            filter_post="/api/{model_slug}/filterQuestionnaires",
            create_with_data_post="/api/{model_slug}/createWithData",
            insert="/api/{model_slug}/create",
            create_instances_from_questionnaires_post="/api/{model_slug}/createInstancesFromQuestionnaires",
            create_instances_from_questionnaires_return_instance="/api/{model_slug}/createInstancesFromQuestionnairesReturnInstances",
            upload_post="/api/{model_slug}/upload",
            upload_bulk_email_assignment_post="/api/{model_slug}/uploadBulkEmailAssignment/{questionnaireId}",
            get_updatable_instances_get="/api/{model_slug}/getUpdatableInstances/{questionnaireId}",
            update_assigned_instances_put="/api/{model_slug}/updateAssignedInstances",
            export_get="/api/{model_slug}/exportQuestionnaire/{questionnaireId}",
            export_example_get="/api/{model_slug}/exportQuestionnaireExample",
            export_responses_post="/api/{model_slug}/exportQuestionnaireResponses",
        )

    @classmethod
    def create_instances_from_questionnaires(cls, payload: dict) -> Optional[List[QuestionnaireInstance]]:
        """
        Creates instances from questionnaires.
        :param payload: The payload to send to the API.
        :return: The response from the API or None
        :rtype: Optional[List[QuestionnaireInstance]]
        """
        endpoint = cls.get_endpoint("create_instances_from_questionnaires_return_instance")
        response = cls._get_api_handler().post(endpoint.format(model_slug=cls._module_slug), data=payload)

        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            response_json = response.json()
            return [QuestionnaireInstance(**instance) for instance in response_json.get("createdInstances", [])]
        logger.info("Failed to create instances from questionnaires %i - %s", response.status_code, response.text)
        return None

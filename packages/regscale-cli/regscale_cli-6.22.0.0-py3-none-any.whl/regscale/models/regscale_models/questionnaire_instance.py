"""
This module contains the QuestionnaireInstances model.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, Field
from requests import Response

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger(__name__)


class QuestionnaireInstanceState(str, Enum):
    """
    Enum for the QuestionnaireInstanceState field in the QuestionnaireInstances model.
    """

    Open = 0
    Submitted = 10
    Accepted = 20
    RequestChanges = 30
    Closed = 40


class QuestionnaireInstance(RegScaleModel):
    """
    A class to represent the QuestionnaireInstances model in RegScale.
    """

    _module_slug = "questionnaireInstances"

    id: int = 0
    parentId: int = 0
    parentModule: Optional[str] = None
    token: Optional[int] = 0
    title: Optional[str] = None
    parentQuestionnaireId: int
    activeStatus: bool = True
    passingStatus: int = 0
    instanceState: int = 0
    uuid: Optional[str] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1
    isPublic: bool = True
    jsonData: Optional[str] = None  # Adjust the type if it's not a string
    assigneeId: Optional[str] = None
    recurrence: Optional[str] = None  # Adjust the type if it's not a string
    dueDate: Optional[str] = None
    sections: Optional[List[int]] = Field(default_factory=list)  # Adjust the type if it's not a string
    rules: Optional[str] = None  # Adjust the type if it's not a string
    emailList: Optional[str] = None  # Adjust the type if it's not a string
    loginRequired: bool = True
    accessCode: Optional[str] = None
    questionnaireIds: Optional[List[int]] = None
    percentComplete: Optional[int] = None
    questions: Optional[List[Dict]] = None  # Adjust the type if it's not a string

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the QuestionnaireInstances model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/getCount",
            graph="/api/{model_slug}/graph",
            filter_questionnaire_instances="/api/{model_slug}/filterQuestionnaireInstances",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{parentQuestionnaireId}",
            link_questionnaire_instance_post="/api/{model_slug}/link",
            link_feedback="/api/{model_slug}/linkFeedback/{id}",
            is_login_required="/api/{model_slug}/isLoginRequired/{uuid}",
            update_responses="/api/{model_slug}/updateResponses/{uuid}",
            update_feedback="/api/{model_slug}/updateFeedback/{uuid}",
            change_state_accepted="/api/{model_slug}/changeStateAccepted/{uuid}",
            change_state_rejected="/api/{model_slug}/changeStateRejected/{uuid}",
            submit_for_feedback="/api/{model_slug}/submitForFeedback/{uuid}",
            reopen_instance="/api/{model_slug}/reopenInstance/{uuid}",
            export_questionnaire_instance="/api/{model_slug}/exportQuestionnaireInstance/{questionnaireInstanceId}",
            create_instances_from_questionnaires_post="/api/questionnaires/createInstancesFromQuestionnaires",
        )

    def create_instances_from_questionnaires(self) -> Optional[Dict]:
        """
        Creates instances from questionnaires.

        :return: The response from the API or None
        :rtype: Optional[Dict]
        """
        endpoint = self.get_endpoint("create_instances_from_questionnaires_post")
        headers = {
            "Content-Type": "application/json-patch+json",
            "Authorization": self._get_api_handler().config.get("token"),
            "accept": "*/*",
            "origin": self._get_api_handler().config.get("domain"),
        }
        response = self._get_api_handler().post(endpoint, headers=headers, data=self.dict())

        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return response.json()
        else:
            logger.info(f"Failed to create instances from questionnaires {response.status_code} - {response.text}")
        return None

    @classmethod
    def _handle_response(cls, response: Optional[Response]) -> Optional[Dict[str, Any]]:
        """
        Helper method to handle API responses consistently.

        :param Optional[Response] response: The response from the API
        :return: The JSON response if successful, None otherwise
        :rtype: Optional[Dict[str, Any]]
        """
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return response.json()
        return None

    @classmethod
    def submit_for_feedback(cls, quid: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Submits a questionnaire instance for feedback.

        :param str quid: The QUID of the questionnaire instance
        :param Dict[str, Any] payload: The data to be sent in the request body
        :return: The response from the API or None
        :rtype: Optional[Dict[str, Any]]
        """
        endpoint = cls.get_endpoint("submit_for_feedback").format(model_slug=cls._module_slug, uuid=quid)
        response = cls._get_api_handler().put(endpoint, data=payload)
        return cls._handle_response(response)

    @classmethod
    def update_response(cls, quid: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates questionnaire instance responses.

        :param str quid: The QUID of the questionnaire instance
        :param Dict[str, Any] payload: The data to be sent in the request body containing instance and questions
        :return: The response from the API or None
        :rtype: Optional[Dict[str, Any]]
        """
        endpoint = cls.get_endpoint("update_responses").format(model_slug=cls._module_slug, uuid=quid)
        response = cls._get_api_handler().put(endpoint, data=payload)
        return cls._handle_response(response)

    @classmethod
    def get_all_by_parent(cls, parent_questionnaire_id: int) -> List["QuestionnaireInstance"]:
        """
        Retrieves all questionnaire instances of a parent questionnaire.

        :param int parent_questionnaire_id: The ID of the parent questionnaire
        :return: A list of questionnaire instances or None
        :rtype: List[QuestionnaireInstance]
        """
        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_all_by_parent").format(
                model_slug=cls._module_slug,
                parentQuestionnaireId=parent_questionnaire_id,
            )
        )
        if not response or response.status_code in [204, 404]:
            return []
        if response and response.ok:
            return [cls(**item) for item in response.json()]
        return []

    @classmethod
    def filter(cls, payload: Dict) -> Optional[List["QuestionnaireInstance"]]:
        """
        Filters questionnaire instances based on the payload.

        :param Dict payload: The data to be sent in the request body
        :return: A list of questionnaire instances or None
        :rtype: Optional[List[QuestionnaireInstance]]
        """
        endpoint = cls.get_endpoint("filter_questionnaire_instances").format(model_slug=cls._module_slug)
        response = cls._get_api_handler().post(endpoint, data=payload)

        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            data = response.json()
            items = data.get("items")
            total = data.get("totalItems")
            logger.info(f"Found Total Change Questionnaires accepted: {total}")
            return [cls(**item) for item in items]
        return None

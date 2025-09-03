"""
This module contains the Questions model for RegScale.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import ConfigDict, Field

from regscale.core.app.utils.api_handler import APIRetrieveError
from regscale.core.app.utils.app_utils import get_current_datetime

from .regscale_model import RegScaleModel


class QuestionType(str, Enum):
    """
    Enum for the QuestionType field in the Questions model.
    """

    ShortAnswer = 0
    LongAnswer = 1
    Instructional = 2
    Date = 3
    PhoneNumber = 4
    Email = 5
    DigitalSignature = 6
    MultipleChoice = 10
    CheckBoxes = 20
    Dropdown = 30
    FileAccess = 50


class AnswerOptions(RegScaleModel):
    answerOption: Optional[str]
    answerScore: Optional[int] = 0


class Questions(RegScaleModel):
    """
    A class to represent the Questions model in RegScale.
    """

    _module_slug = "questions"

    id: Optional[int] = None
    parentQuestionnaireId: int = 0
    uuid: Optional[str] = None
    questionType: int = 0
    name: Optional[str] = None
    label: Optional[str] = None
    prompt: Optional[str] = None
    tenantsId: Optional[int] = 1
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    isPublic: bool = True
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    controlNumber: Optional[str] = None
    section: int = 0
    staticAnswerOptions: Optional[List[Dict]] = None  # Adjust the type if it's not a string
    askQuestion: bool = True
    quid: Optional[str] = None
    required: bool = True
    sectionIndex: int = 1
    uploadEnabled: bool = False
    response: Optional[str] = None  # Adjust the type if it's not a string

    @classmethod
    def get_all_by_parent(cls, parent_questionnaire_id: int) -> List["Questions"]:
        """
        Retrieve all questions associated with a parent questionnaire.

        :param parent_questionnaire_id: The ID of the parent questionnaire to fetch questions for.
        :return: A list of Questions objects associated with the parent questionnaire.
        :raises ValueError: If parent_questionnaire_id is less than or equal to 0.
        :raises APIRetrieveError: If the API request fails.
        """
        if parent_questionnaire_id <= 0:
            raise ValueError("parent_questionnaire_id must be a positive integer")

        params = {"parentId": parent_questionnaire_id}
        endpoint = cls.get_endpoint("get_all_by_parent").format(
            model_slug=cls._module_slug,
        )

        response = cls._get_api_handler().get(endpoint=endpoint, params=params)
        if not response.ok:
            raise APIRetrieveError(f"Failed to fetch questions: {response.status_code} - {response.text}")

        return [cls(**ques) for ques in response.json()]

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get endpoints for the Question model.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getAllByParent",
            get="/api/{model_slug}/find/{id}",
            insert="/api/{model_slug}/create",
            update="/api/{model_slug}/update",
            delete="/api/{model_slug}/delete/{id}",
            get_new_section_index_post="/api/{model_slug}/getNewSectionIndex",
            update_origin_section_put="/api/{model_slug}/updateOriginSection",
            section_update_from_insert_put="/api/{model_slug}/sectionUpdateFromInsert",
            section_update_from_cancel_put="/api/{model_slug}/sectionUpdateFromCancel",
            index_up_put="/api/{model_slug}/indexUp",
            index_down_put="/api/{model_slug}/indexDown",
        )

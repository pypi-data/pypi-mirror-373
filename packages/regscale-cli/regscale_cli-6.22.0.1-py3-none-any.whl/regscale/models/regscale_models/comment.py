"""This module contains the Comment model class."""

from typing import Optional

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from .regscale_model import RegScaleModel


class Comment(RegScaleModel):
    """
    Comment model class
    """

    _module_slug = "comments"
    _unique_fields = [
        ["comment", "parentID", "parentModule"],
    ]
    _parent_id_field = "parentID"

    id: int = 0
    comment: str
    commentDate: Optional[str] = None
    parentID: int = 0
    parentModule: Optional[str] = None
    userId: str = Field(default_factory=RegScaleModel.get_user_id)
    tenantsId: int = 1
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    isPublic: bool = True
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    partId: Optional[int] = None
    partType: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Comments model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_part="/api/comments/getAllByPart/{intParentID}/{strModule}/{strType}/{strPart}",
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
        )

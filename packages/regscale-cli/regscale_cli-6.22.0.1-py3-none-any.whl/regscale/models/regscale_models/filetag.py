from enum import Enum
from typing import Optional

from pydantic import Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class TagTypeEnum(Enum):
    """
    TagTypeEnum class
    """

    SYSTEM = "System"
    EXPORT = "Export"
    IMPORT = "Import"
    DATA = "Data"
    USER = "User"


class FileTag(RegScaleModel):
    _module_slug = "filetags"

    id: int = 0
    uuid: Optional[str] = None
    title: str = ""  # required
    tagType: TagTypeEnum = TagTypeEnum.USER.value  # default to user. Use System for Export or Import
    isPublic: bool = True
    OscalRequired: bool = False
    tagColor: Optional[str] = None  # not currently implemented yet
    tagTextColor: Optional[str] = None  # not currently implemented yet
    tenantsId: int = 1
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

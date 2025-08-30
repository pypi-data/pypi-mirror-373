from pydantic import Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class TagMapping(RegScaleModel):
    _module_slug = "tagMappings"

    id: int = 0
    parentId: str = ""
    parentModule: str = ""
    tagId: int = 0
    isPublic: bool = True
    tenantsId: int = 1
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

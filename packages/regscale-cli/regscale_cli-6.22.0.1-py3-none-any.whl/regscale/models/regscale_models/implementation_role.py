import logging
from typing import Optional

from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class ImplementationRole(RegScaleModel):
    """Class for a RegScale SystemRoles"""

    _module_slug = "implementingRoles"

    id: Optional[int] = None
    uuid: Optional[str] = None
    parentId: int  # Required Field
    parentModule: str  # Required Field
    roleId: int  # Required Field
    isPublic: bool = True

    @staticmethod
    def add_role(role_id: int, control_implementation_id: int, parent_module: str) -> "ImplementationRole":
        """
        Add a role to a control implementation

        :param int role_id: The ID of the role to add
        :param int control_implementation_id: The ID of the control implementation to add the role to
        :param str parent_module: The parent module of the role
        :return: The new role
        :rtype: ImplementationRole
        """
        role = ImplementationRole(roleId=role_id, parentId=control_implementation_id, parentModule=parent_module)
        return role.create()

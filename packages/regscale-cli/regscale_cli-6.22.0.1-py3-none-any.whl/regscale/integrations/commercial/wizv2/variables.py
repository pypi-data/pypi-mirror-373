#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wiz Variables"""

from regscale.core.app.utils.variables import RsVariableType, RsVariablesMeta
from regscale.integrations.commercial.wizv2.constants import RECOMMENDED_WIZ_INVENTORY_TYPES, DEFAULT_WIZ_HARDWARE_TYPES


class WizVariables(metaclass=RsVariablesMeta):
    """
    Wiz Variables class to define class-level attributes with type annotations and examples
    """

    # Define class-level attributes with type annotations and examples
    wizFullPullLimitHours: RsVariableType(int, 8)  # type: ignore
    wizUrl: RsVariableType(str, "https://api.us27.app.wiz.io/graphql", required=False)  # type: ignore
    wizIssueFilterBy: RsVariableType(
        str,
        '{"projectId": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"], "type": ["API_GATEWAY"]}',
        default={},
        required=False,
    )  # type: ignore
    wizInventoryFilterBy: RsVariableType(
        str,
        '{"projectId": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"], "type": ["API_GATEWAY"]}',
        default="""{"type": ["%s"] }""" % '","'.join(RECOMMENDED_WIZ_INVENTORY_TYPES),  # type: ignore
    )  # type: ignore
    wizAccessToken: RsVariableType(str, "", sensitive=True, required=False)  # type: ignore
    wizClientId: RsVariableType(str, "", sensitive=True)  # type: ignore
    wizClientSecret: RsVariableType(str, "", sensitive=True)  # type: ignore
    wizLastInventoryPull: RsVariableType(str, "2022-01-01T00:00:00Z", required=False)  # type: ignore
    useWizHardwareAssetTypes: RsVariableType(bool, False, required=False)  # type: ignore
    wizHardwareAssetTypes: RsVariableType(
        list,
        '["CONTAINER", "CONTAINER_IMAGE", "VIRTUAL_MACHINE", "VIRTUAL_MACHINE_IMAGE", "DB_SERVER", '
        '"CLIENT_APPLICATION", "SERVER_APPLICATION", "VIRTUAL_APPLIANCE"]',
        default=DEFAULT_WIZ_HARDWARE_TYPES,
        required=False,
    )  # type: ignore
    wizReportAge: RsVariableType(int, "14", default=14, required=False)  # type: ignore

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DuroSuite Variables"""

from regscale.core.app.utils.variables import RsVariableType, RsVariablesMeta


class DuroSuiteVariables(metaclass=RsVariablesMeta):
    """
    DuroSuite Variables class to define class-level attributes with type annotations and examples
    """

    # Define class-level attributes with type annotations and examples
    duroSuiteURL: RsVariableType(str, "https://example.com")  # type: ignore # noqa: F722
    duroSuiteUser: RsVariableType(str, "user")  # type: ignore # noqa: F722,F821
    duroSuitePassword: RsVariableType(str, "password", sensitive=True)  # type: ignore # noqa: F722,F821
    duroSuiteDemoHost: RsVariableType(str, "ip_address")  # type: ignore # noqa: F722,F821
    # Palo Alto device credentials
    duroSuitePaloAltoUser: RsVariableType(str, "admin", required=False)  # type: ignore # noqa: F722,F821
    duroSuitePaloAltoPassword: RsVariableType(str, "password", sensitive=True, required=False)  # type: ignore # noqa: F722,F821
    duroSuiteEnabled: RsVariableType(bool, "true", default=False)  # type: ignore # noqa: F722,F821

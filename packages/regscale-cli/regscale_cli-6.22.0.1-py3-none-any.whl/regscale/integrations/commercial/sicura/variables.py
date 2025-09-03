#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DuroSuite Variables"""

from regscale.core.app.utils.variables import RsVariableType, RsVariablesMeta


class SicuraVariables(metaclass=RsVariablesMeta):
    """
    Sicura Variables class to define class-level attributes with type annotations and examples
    """

    # Define class-level attributes with type annotations and examples
    sicuraEnabled: RsVariableType(bool, "True", default=False)  # type: ignore # noqa: F722,F821
    sicuraURL: RsVariableType(str, "https://sicura.mydomain.com")  # type: ignore # noqa: F722,F821
    sicuraToken: RsVariableType(str, "your-sicura-token")  # type: ignore # noqa: F722,F821

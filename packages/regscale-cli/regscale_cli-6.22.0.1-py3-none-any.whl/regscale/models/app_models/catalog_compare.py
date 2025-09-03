#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass for a RegScale Assessment"""
import re
import sys
from dataclasses import asdict, dataclass
from typing import Any, Optional

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger


@dataclass
class CatalogCompare:
    """Catalog comparison Model"""

    title: Optional[str] = None
    uuid: Optional[str] = None
    keywords: Optional[list] = None
    cci_count: int = 0
    objective_count: int = 0
    parameter_count: int = 0
    security_control_count: int = 0
    test_count: int = 0

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from CatalogCompare

        :param Any key: Key to get value from
        :return: value of provided key
        :rtype: Any
        """
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in CatalogCompare with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :rtype: None
        """
        return setattr(self, key, value)

    def dict(self) -> dict:
        """
        Create a dictionary from the CatalogCompare dataclass

        :return: Dictionary of CatalogCompare
        :rtype: dict
        """
        return {k: v for k, v in asdict(self).items()}

    @staticmethod
    def from_new_catalog_dict(obj: dict, keywords: list = None) -> "CatalogCompare":
        """
        Create CatalogCompare object from dict

        :param dict obj: dictionary of a newly formatted catalog
        :param list keywords: list of keywords for the catalog
        :return: CatalogCompare class
        :rtype: CatalogCompare
        """
        _title = str(obj["catalog"].get("title", "")) or None
        _uuid = str(obj["catalog"].get("uuid", "")) or None
        _keywords = keywords
        _cci_count = 0
        _objective_count = 0
        _parameter_count = 0
        _test_count = 0
        _security_control_count = 0
        for control in obj["catalog"].get("securityControls", []):
            _objective_count += len(control.get("objectives", []))
            _cci_count += len(control.get("cci", []))
            _parameter_count += len(control.get("parameters", []))
            _test_count += len(control.get("tests", []))
            _security_control_count += 1

        return CatalogCompare(
            title=_title,
            uuid=_uuid,
            keywords=_keywords,
            cci_count=_cci_count,
            objective_count=_objective_count,
            parameter_count=_parameter_count,
            security_control_count=_security_control_count,
            test_count=_test_count,
        )

    @staticmethod
    def from_old_catalog_dict(obj: dict, keywords: list = None) -> "CatalogCompare":
        """
        Create CatalogCompare object from dict

        :param dict obj: dictionary of an old formatted catalog
        :param list keywords: list of keywords for the catalog
        :return: CatalogCompare class
        :rtype: CatalogCompare
        """
        _title = str(obj.get("title", "")) or None
        _uuid = str(obj.get("uuid", "")) or None
        _keywords = keywords
        _cci_count = int(obj.get("cci", 0)) or 0
        _objective_count = int(obj.get("objectives", 0)) or 0
        _parameter_count = int(obj.get("parameters", 0)) or 0
        _security_control_count = int(obj.get("securityControls", 0)) or 0
        _test_count = int(obj.get("tests", 0)) or 0

        return CatalogCompare(
            title=_title,
            uuid=_uuid,
            keywords=_keywords,
            cci_count=_cci_count,
            objective_count=_objective_count,
            parameter_count=_parameter_count,
            security_control_count=_security_control_count,
            test_count=_test_count,
        )

    @staticmethod
    def run_new_diagnostics(
        new_diagnose_cat: dict,
    ) -> "CatalogCompare":
        """
        Run diagnostics on new catalog

        :param dict new_diagnose_cat: dictionary of the new catalog
        :return: CatalogCompare class
        :rtype: CatalogCompare
        """
        new_list = []
        # get keywords list from catalog
        # https://stackoverflow.com/questions/4998629/split-string-with-multiple-delimiters-in-python
        keywords_list = re.split(r"; |, |\*|\n", new_diagnose_cat.get("keywords", ""))
        for keyword in keywords_list:
            new_key = keyword.replace("<p>", "").replace("</p>", "").lstrip()
            new_list.append(new_key)

        return CatalogCompare().from_new_catalog_dict(new_diagnose_cat, new_list)

    @staticmethod
    def run_old_diagnostics(
        old_diagnose_cat: dict,
    ) -> "CatalogCompare":
        """
        Function to run diagnostics on the old catalog

        :param dict old_diagnose_cat: dictionary of the old catalog
        :return: CatalogCompare object
        :rtype: CatalogCompare
        """
        # set variables for catalog section
        cci_count = 0
        objective_count = 0
        parameter_count = 0
        test_count = 0
        new_list = []
        # get keywords list from catalog
        # https://stackoverflow.com/questions/4998629/split-string-with-multiple-delimiters-in-python
        keywords_list = re.split(r"; |, |\*|\n", old_diagnose_cat.get("keywords", ""))
        for keyword in keywords_list:
            new_key = keyword.replace("<p>", "").replace("</p>", "").lstrip()
            new_list.append(new_key)
        # loop through security controls
        for control in old_diagnose_cat["securityControls"]:
            # count objectives in security controls
            for objectives in control["objectives"]:
                if objectives.get("uuid"):
                    objective_count += 1
            # count parametes in security controls
            for parameters in control["parameters"]:
                if parameters.get("uuid"):
                    parameter_count += 1
            # count ccis in security controls
            for ccis in control["cci"]:
                if ccis.get("uuid"):
                    cci_count += 1
            # count tests in security controls
            for tests in control["tests"]:
                if tests.get("uuid"):
                    test_count += 1
        return CatalogCompare(
            title=old_diagnose_cat.get("title", ""),
            uuid=old_diagnose_cat.get("uuid", ""),
            keywords=new_list,
            cci_count=cci_count,
            objective_count=objective_count,
            parameter_count=parameter_count,
            security_control_count=len(old_diagnose_cat.get("securityControls", 0)),
            test_count=test_count,
        )

    @staticmethod
    def get_master_catalogs(api: Api) -> dict:
        """
        Get list of master catalogs via API

        :param Api api: API object
        :return: master catalog list
        :rtype: dict
        """
        catalog_url = "https://regscaleblob.blob.core.windows.net/catalogs/catalog_registry.json"
        response = api.get(url=catalog_url, headers={})
        try:
            master_list = response.json()
        except Exception:
            logger = create_logger()
            logger.error("Unable to retrieve master catalogs.")
            sys.exit(1)
        # Filter out catalogs without downloadURL
        master_list["catalogs"] = [cat for cat in master_list.get("catalogs") if cat.get("downloadURL")]
        return master_list

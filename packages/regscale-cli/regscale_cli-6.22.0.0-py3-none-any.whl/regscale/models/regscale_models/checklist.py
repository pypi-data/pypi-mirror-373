#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for a RegScale Security Checklist"""
import warnings
from enum import Enum
from json import JSONDecodeError
from typing import Any, List, Optional, Union
from urllib.parse import urljoin

from pydantic import ConfigDict, Field

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ChecklistTool(str, Enum):
    Ansible = "Ansible"
    Chef = "Chef"
    CISBenchmarks = "CIS Benchmarks"
    MITRESAF = "MITRE SAF"
    Puppet = "Puppet"
    SCAP = "SCAP"
    SIEM = "SIEM"
    STIGs = "STIGs"
    VulnerabilityScanner = "Vulnerability Scanner"
    Other = "Other"


class ChecklistStatus(str, Enum):
    FAIL = "Fail"
    PASS = "Pass"
    NOT_APPLICABLE = "Not Applicable"
    NOT_REVIEWED = "Not Reviewed"


class Checklist(RegScaleModel):
    """RegScale Checklist

    :return: RegScale Checklist
    """

    _module_slug = "securitychecklist"
    _module_string = "securitychecklists"
    # Should we include baseline, ruleId, check, and results in unique fields?
    _unique_fields = [
        [
            "assetId",
            "tool",
            "vulnerabilityId",
        ],
    ]
    _parent_id_field = "assetId"
    # Required
    id: int = 0
    status: Union[ChecklistStatus, str]
    assetId: int
    tool: Union[ChecklistTool, str]
    baseline: str
    vulnerabilityId: str
    results: str
    check: str
    version: Optional[str] = None
    uuid: Optional[str] = None
    ruleId: Optional[str] = None
    cci: Optional[str] = None
    comments: Optional[str] = None
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    datePerformed: Optional[str] = None
    isPublic: bool = True
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Override RegScaleModel and get additional endpoints for the Checklist model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
        )

    def __hash__(self) -> hash:
        """
        Enable object to be hashable

        :return: Hashed Checklist
        :rtype: hash
        """
        return hash(
            (
                self.tool,
                self.vulnerabilityId,
                self.ruleId,
                self.baseline,
                self.check,
                self.results,
                self.comments,
                self.assetId,
            )
        )

    def __eq__(self, other: object) -> bool:
        """
        Compare Checklists

        :param object other: Checklist to compare against
        :return: True if equal, False if not
        :rtype: bool
        """
        return (
            # Unique values
            # Tool, VulnerabilityId, RuleId, Baseline, [Check], Results, Comments, Status, AssetId,
            # TenantsId, CCI, Version
            self.tool == other.tool
            and self.vulnerabilityId == other.vulnerabilityId
            and self.ruleId == other.ruleId
            and self.baseline == other.baseline
            and self.check == other.check
            and self.results == other.results
            and self.comments == other.comments
            and self.assetId == other.assetId
        )

    def __delitem__(self, key: Any) -> None:
        """
        Delete an item from the Checklist

        :param Any key: Key to delete
        :rtype: None
        """
        del self[key]

    @staticmethod
    def insert_or_update_checklist(
        app: Application,
        new_checklist: "Checklist",
        existing_checklists: list[Any],
    ) -> Optional[int]:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use the create_or_update method instead.

        Insert or update a checklist

        :param Application app: RegScale Application instance
        :param Checklist new_checklist: New checklist to insert or update
        :param list[Any] existing_checklists: Existing checklists to compare against
        :return: int of the checklist id or None
        :rtype: Optional[int]
        """
        warnings.warn(
            "insert_or_update_checklist is deprecated and will be removed in a future version. "
            "Use create_or_update method instead.",
            DeprecationWarning,
        )
        delete_keys = [
            "asset",
            "uuid",
            "lastUpdatedById",
            "dateLastUpdated",
            "createdById",
            "dateCreated",
        ]
        for dat in existing_checklists:
            for key in delete_keys:
                if key in dat:
                    del dat[key]
        api = Api()
        if matching_checklists := [
            Checklist(**chk) for chk in existing_checklists if Checklist(**chk) == new_checklist
        ]:
            app.logger.info("Updating checklist %s...", new_checklist.baseline)
            new_checklist.id = matching_checklists[0].id
            res = api.put(
                url=urljoin(app.config["domain"], f"/api/securitychecklist/{new_checklist.id}"),
                json=new_checklist.dict(),
            )
        else:
            app.logger.info("Inserting checklist %s", new_checklist.baseline)
            res = api.post(
                url=urljoin(app.config["domain"], "/api/securitychecklist"),
                json=new_checklist.dict(),
            )
        if res.status_code != 200:
            app.logger.warning("Unable to insert or update checklist %s", new_checklist.baseline)
            return None
        return res.json()["id"]

    @staticmethod
    def batch_insert_or_update(
        api: Api, checklists: list["Checklist"], method: Optional[str] = "insert"
    ) -> Optional[list["Checklist"]]:
        """
        Insert a batch of checklists

        :param Api api: RegScale API instance
        :param list[Checklist] checklists: List of checklists to insert
        :param Optional[str] method: Method to use (insert or update), defaults to insert
        :return: List of checklists inserted
        :rtype: Optional[list[Checklist]]
        """
        if method == "insert":
            endpoint = "batchCreate"
            api.logger.info("Creating %i checklist(s) in RegScale...", len(checklists))
        elif method == "update":
            endpoint = "batchUpdate"
            api.logger.info("Updating %i checklist(s) in RegScale...", len(checklists))
        else:
            api.logger.error("Invalid method %s, please use insert or update.", method)
            return None
        response = api.post(
            url=urljoin(api.app.config["domain"], f"/api/securityChecklist/{endpoint}"),
            json=[check.dict() for check in checklists],
        )
        if response.ok:
            try:
                return [Checklist(**check) for check in response.json()]
            except TypeError as err:
                api.logger.error("Unable to convert checklist(s): %s", err)
                return None
            except JSONDecodeError:
                api.logger.error("Unable to %s checklist(s) in batch: %s", method, response.text)
                return None
        else:
            api.logger.error(
                "Unable to %s checklist(s) in batch: %i: %s %s",
                method,
                response.status_code,
                response.reason,
                response.text,
            )
            response.raise_for_status()
        return None

    @staticmethod
    def analyze_and_batch_process(
        app: Application,
        new_checklists: Optional[list[dict]] = None,
        existing_checklists: Optional[list["Checklist"]] = None,
    ) -> dict:
        """
        Function to insert or update a checklist using batches via API

        :param Application app: RegScale CLI Application instance
        :param Optional[list[dict]] new_checklists: List of new checklists to insert or update
        :param Optional[list[Checklist]] existing_checklists: List of existing checklists to compare against
        :return: Dictionary with list of checklists inserted and/or updated
            example: {'inserted': [], 'updated': [Checklist()...]}
        :rtype: dict
        """
        if not new_checklists:
            new_checklists = []

        api = Api()
        results = {"inserted": [], "updated": []}  # type: dict
        # if no existing checklists, insert all new checklists and return results
        if existing_checklists is None:
            results["inserted"] = Checklist.batch_insert_or_update(api, new_checklists, "insert")
            return results
        # see if any of the new checklists already exist
        update_checks = []
        create_checks = []
        for new_checklist in new_checklists:
            if matching_checklists := [
                check for check in existing_checklists if check.vulnerabilityId == new_checklist.vulnerabilityId
            ]:
                new_checklist.id = matching_checklists[0].id
                update_checks.append(new_checklist)
            else:
                create_checks.append(new_checklist)
        if update_checks:
            results["updated"] = Checklist.batch_insert_or_update(api, update_checks, "update")
        if create_checks:
            results["inserted"] = Checklist.batch_insert_or_update(api, create_checks, "insert")
        return results

    @classmethod
    def get_checklists_by_asset(cls, api: Api, asset_id: int) -> List["Checklist"]:  # noqa
        """
        Return all checklists for a given RegScale parent id and parent module

        :param Api api: RegScale CLI API instance
        :param int asset_id: RegScale Asset ID
        :return: List of checklists for the given asset_id
        :rtype: List[Checklist]
        """
        api.logger.info("Fetching all checklists for RegScale asset #%i...", asset_id)
        response = api.get(
            url=urljoin(
                api.config.get("domain"),
                f"/api/securityChecklist/getAllByParent/{asset_id}",
            )
        )
        try:
            if checklists := [Checklist(**check) for check in response.json()]:
                api.logger.info(
                    "Found %i checklist(s) for asset #%i in RegScale.",
                    len(checklists),
                    asset_id,
                )
                return checklists
        except TypeError as err:
            api.logger.error("Unable to convert checklist(s): %s", err)
        except JSONDecodeError:
            api.logger.error(
                "Unable to retrieve any checklists for asset #%i.\n%i: %s-%s",
                asset_id,
                response.status_code,
                response.reason,
                response.text,
            )
        return []

    @staticmethod
    def get_checklists(parent_id: int, parent_module: str = "components") -> List[dict]:
        """
        Return all checklists for a given RegScale parent id and parent module

        :param int parent_id: RegScale parent id
        :param str parent_module: RegScale parent module, defaults to components
        :return: List of checklists for the given parent id and module
        :rtype: List[dict]
        """
        app = Application()
        api = Api()
        app.logger.debug("Fetching all checklists for %s %s", parent_module, parent_id)
        checklists = []
        query = """
                           query {
                securityChecklists(skip: 0, take: 50,where:{asset: {parentId: {eq: parent_id_placeholder}, parentModule: {eq: "parent_module_placeholder"}}}) {
                    items {
                            id
                            asset {
                              id
                              name
                              parentId
                              parentModule
                            }
                            status
                            tool
                            datePerformed
                            vulnerabilityId
                            ruleId
                            cci
                            check
                            results
                            baseline
                            comments
                    }
                    totalCount
                    pageInfo {
                        hasNextPage
                    }
                }
            }
            """.replace(
            "parent_id_placeholder", str(parent_id)
        ).replace(
            "parent_module_placeholder", parent_module
        )
        data = api.graph(query)
        if "securityChecklists" in data and "items" in data["securityChecklists"]:
            for item in data["securityChecklists"]["items"]:
                item["assetId"] = item["asset"]["id"]
                checklists.append(item)
        return checklists

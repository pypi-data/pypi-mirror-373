#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wiz v2 Integration Models (RegScale pattern)."""

from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from regscale.models import regscale_models


class AssetCategory(Enum):
    """Map Wiz assetTypes with RegScale assetCategories."""

    SERVICE_USAGE_TECHNOLOGY = regscale_models.AssetCategory.Hardware
    GATEWAY = regscale_models.AssetCategory.Hardware
    SECRET = regscale_models.AssetCategory.Hardware
    BUCKET = regscale_models.AssetCategory.Hardware
    WEB_SERVICE = regscale_models.AssetCategory.Hardware
    DB_SERVER = regscale_models.AssetCategory.Hardware
    LOAD_BALANCER = regscale_models.AssetCategory.Hardware
    CLOUD_ORGANIZATION = regscale_models.AssetCategory.Hardware
    SUBNET = regscale_models.AssetCategory.Hardware
    VIRTUAL_MACHINE = regscale_models.AssetCategory.Hardware
    TECHNOLOGY = regscale_models.AssetCategory.Hardware
    SECRET_CONTAINER = regscale_models.AssetCategory.Hardware
    FILE_SYSTEM_SERVICE = regscale_models.AssetCategory.Hardware
    KUBERNETES_CLUSTER = regscale_models.AssetCategory.Hardware
    ROUTE_TABLE = regscale_models.AssetCategory.Hardware
    COMPUTE_INSTANCE_GROUP = regscale_models.AssetCategory.Hardware
    HOSTED_TECHNOLOGY = regscale_models.AssetCategory.Hardware
    USER_ACCOUNT = regscale_models.AssetCategory.Hardware
    DNS_ZONE = regscale_models.AssetCategory.Hardware
    VOLUME = regscale_models.AssetCategory.Hardware
    SERVICE_ACCOUNT = regscale_models.AssetCategory.Hardware
    RESOURCE_GROUP = regscale_models.AssetCategory.Hardware
    ACCESS_ROLE = regscale_models.AssetCategory.Hardware
    SUBSCRIPTION = regscale_models.AssetCategory.Hardware
    SERVICE_CONFIGURATION = regscale_models.AssetCategory.Hardware
    VIRTUAL_NETWORK = regscale_models.AssetCategory.Hardware
    VIRTUAL_MACHINE_IMAGE = regscale_models.AssetCategory.Hardware
    FIREWALL = regscale_models.AssetCategory.Hardware
    DATABASE = regscale_models.AssetCategory.Hardware
    GOVERNANCE_POLICY_GROUP = regscale_models.AssetCategory.Hardware
    STORAGE_ACCOUNT = regscale_models.AssetCategory.Hardware
    CONFIG_MAP = regscale_models.AssetCategory.Hardware
    NETWORK_ADDRESS = regscale_models.AssetCategory.Hardware
    NETWORK_INTERFACE = regscale_models.AssetCategory.Hardware
    DAEMON_SET = regscale_models.AssetCategory.Hardware
    PRIVATE_ENDPOINT = regscale_models.AssetCategory.Hardware
    ENDPOINT = regscale_models.AssetCategory.Hardware
    DEPLOYMENT = regscale_models.AssetCategory.Hardware
    POD = regscale_models.AssetCategory.Hardware
    KUBERNETES_STORAGE_CLASS = regscale_models.AssetCategory.Hardware
    ACCESS_ROLE_BINDING = regscale_models.AssetCategory.Hardware
    KUBERNETES_INGRESS = regscale_models.AssetCategory.Hardware
    CONTAINER = regscale_models.AssetCategory.Hardware
    CONTAINER_IMAGE = regscale_models.AssetCategory.Hardware
    CONTAINER_REGISTRY = regscale_models.AssetCategory.Hardware
    GOVERNANCE_POLICY = regscale_models.AssetCategory.Hardware
    REPLICA_SET = regscale_models.AssetCategory.Hardware
    KUBERNETES_SERVICE = regscale_models.AssetCategory.Hardware
    KUBERNETES_PERSISTENT_VOLUME_CLAIM = regscale_models.AssetCategory.Hardware
    KUBERNETES_PERSISTENT_VOLUME = regscale_models.AssetCategory.Hardware
    KUBERNETES_NETWORK_POLICY = regscale_models.AssetCategory.Hardware
    KUBERNETES_NODE = regscale_models.AssetCategory.Hardware


class ComplianceCheckStatus(Enum):
    PASS = "Pass"
    FAIL = "Fail"


class ComplianceReport(BaseModel):
    resource_name: str = Field(..., alias="Resource Name")
    cloud_provider_id: str = Field(..., alias="Cloud Provider ID")
    object_type: str = Field(..., alias="Object Type")
    native_type: str = Field(..., alias="Native Type")
    tags: Optional[str] = Field(None, alias="Tags")
    subscription: str = Field(..., alias="Subscription")
    projects: Optional[str] = Field(None, alias="Projects")
    cloud_provider: str = Field(..., alias="Cloud Provider")
    policy_id: str = Field(..., alias="Policy ID")
    policy_short_name: str = Field(..., alias="Policy Short Name")
    policy_description: Optional[str] = Field(None, alias="Policy Description")
    policy_category: Optional[str] = Field(None, alias="Policy Category")
    control_id: Optional[str] = Field(None, alias="Control ID")
    compliance_check: Optional[str] = Field(None, alias="Compliance Check Name (Wiz Subcategory)")
    control_description: Optional[str] = Field(None, alias="Control Description")
    issue_finding_id: Optional[str] = Field(None, alias="Issue/Finding ID")
    severity: Optional[str] = Field(None, alias="Severity")
    result: str = Field(..., alias="Result")
    framework: Optional[str] = Field(None, alias="Framework")
    remediation_steps: Optional[str] = Field(None, alias="Remediation Steps")
    assessed_at: Optional[datetime] = Field(None, alias="Assessed At")
    created_at: Optional[datetime] = Field(None, alias="Created At")
    updated_at: Optional[datetime] = Field(None, alias="Updated At")
    subscription_name: Optional[str] = Field(None, alias="Subscription Name")
    subscription_provider_id: Optional[str] = Field(None, alias="Subscription Provider ID")
    resource_id: str = Field(..., alias="Resource ID")
    resource_region: Optional[str] = Field(None, alias="Resource Region")
    resource_cloud_platform: Optional[str] = Field(None, alias="Resource Cloud Platform")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ECR Model Classes"""


from typing import Dict, List

from pydantic import BaseModel


class Attribute(BaseModel):
    """
    Attribute model
    """

    key: str
    value: str


class Finding(BaseModel):
    """
    Finding model
    """

    name: str
    uri: str
    severity: str
    attributes: List[Attribute]


class ImageScanFindings(BaseModel):
    """
    Image Scan Finding model
    """

    findings: List[Finding]
    imageScanCompletedAt: float
    vulnerabilitySourceUpdatedAt: float
    findingSeverityCounts: Dict[str, int]


class ImageId(BaseModel):
    """
    Image ID model
    """

    imageDigest: str
    imageTag: str


class ImageScanStatus(BaseModel):
    """
    Image Scan Status model
    """

    status: str
    description: str


class Scan(BaseModel):
    """
    Scan model
    """

    imageScanFindings: ImageScanFindings
    registryId: str
    repositoryName: str
    imageId: ImageId
    imageScanStatus: ImageScanStatus

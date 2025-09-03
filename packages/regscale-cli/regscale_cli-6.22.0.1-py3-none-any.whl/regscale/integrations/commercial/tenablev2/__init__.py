"""
Tenable integration for RegScale CLI.

This module provides functionality for scanning assets and findings from Tenable.io and Tenable SC.
"""

from regscale.integrations.commercial.tenablev2.commands import tenable, sync_vulns, sync_jsonl

__all__ = ["tenable", "sync_vulns", "sync_jsonl"]

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from regscale.integrations.scanner_integration import IntegrationAsset

from .variables import DuroSuiteVariables
from regscale.models import regscale_models
from rich.progress import Progress


logger = logging.getLogger("regscale")


def is_palo_alto_device(asset: "IntegrationAsset") -> bool:
    """
    Check if the asset is a Palo Alto device.
    """
    return bool(
        asset.operating_system == regscale_models.AssetOperatingSystem.PaloAlto
        or (asset.software_name and "palo alto" in asset.software_name.lower())
        or (asset.manufacturer and "palo alto" in asset.manufacturer.lower())
    )


def scan_durosuite_devices(asset: "IntegrationAsset", plan_id: int, progress: Optional[Progress] = None) -> None:
    """
    Scan devices using DuroSuite.

    This method checks if an asset is a DuroSuite device and triggers a DuroSuite scan if it is.

    :param IntegrationAsset asset: The asset to check
    :param int plan_id: The ID of the security plan
    :param Optional[Progress] progress: The progress object to use for the scan
    """
    if is_palo_alto_device(asset):
        _handle_palo_alto_device(asset, plan_id, progress)


def _handle_palo_alto_device(asset: "IntegrationAsset", plan_id: int, progress: Optional[Progress] = None) -> None:
    """
    Handle detection and scanning of Palo Alto devices.

    This method checks if an asset is a Palo Alto device and triggers a DuroSuite scan if it is.

    :param IntegrationAsset asset: The asset to check
    :param int plan_id: The ID of the security plan
    :param Optional[Progress] progress: The progress object to use for the scan
    """
    try:
        # Check if this is a Palo Alto device
        if not is_palo_alto_device(asset):
            return

        logger.info(f"Detected Palo Alto device: {asset.name}")

        # Import DuroSuite scanner here to avoid circular imports
        from regscale.integrations.commercial.durosuite.scanner import durosuite_scan, DuroSuiteOS

        # Get the IP address or hostname for the device
        # Try IP address first, then FQDN, then name if it looks like an IP or hostname
        host = None
        if asset.ip_address:
            host = asset.ip_address
        elif asset.fqdn:
            host = asset.fqdn
        elif asset.name and any(c in asset.name for c in ".:"):  # Basic check for IP or hostname format
            host = asset.name

        if not host:
            logger.warning(f"No valid host information found for Palo Alto device {asset.name}")
            return

        # Log the host we're using
        logger.info(f"Using host {host} for Palo Alto device {asset.name}")

        # Get credentials from ScannerVariables
        ansible_user = DuroSuiteVariables.duroSuitePaloAltoUser
        ansible_ssh_pass = DuroSuiteVariables.duroSuitePaloAltoPassword
        ansible_become_pass = ""  # Not needed for Palo Alto devices

        if not ansible_user or not ansible_ssh_pass:
            logger.warning("Palo Alto credentials not configured in ScannerVariables")
            return

        # Trigger DuroSuite scan using the existing progress object
        durosuite_scan(
            host=host,  # Use the host as the device name to ensure proper connection
            os_id=DuroSuiteOS.PALO_ALTO,
            regscale_ssp_id=plan_id,
            ansible_user=ansible_user,
            ansible_ssh_pass=ansible_ssh_pass,
            ansible_become_pass=ansible_become_pass,
            device_name=asset.name,  # Use the asset name as the device name for the scan
            progress=progress,  # Pass the existing progress object
        )
        logger.info(f"Successfully initiated DuroSuite scan for Palo Alto device {asset.name} at {host}")

    except Exception as e:
        logger.error(f"Error handling Palo Alto device {asset.name}: {str(e)}", exc_info=True)
        # Don't raise the exception - we don't want to break the main asset creation flow

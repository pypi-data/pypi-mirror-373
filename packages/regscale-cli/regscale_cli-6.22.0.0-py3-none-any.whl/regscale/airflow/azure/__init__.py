"""Prevent usage and imports that will break when used outside of airflow-azure extra."""

import sys

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    print("To use Azure Blob Storage features, you need to install the [airflow-azure] extra package.")
    sys.exit(1)

"""Provide functions and an entrypoint for uploading DAGs to Azure Blob Storage."""

import os
import sys
from pathlib import Path
from typing import Optional, Union, List, Tuple

from azure.storage.blob import BlobServiceClient

from regscale.core.app.logz import create_logger


def upload_dag_to_blob_storage(
    connection_string: str,
    container_name: str,
    blob_name: str,
    file_path: Union[str, Path],
    exit_on_failure: bool = True,
) -> None:
    """Upload a DAG to Azure Blob Storage

    :param str connection_string: Azure Blob Storage connection string
    :param str container_name: Azure Blob Storage container name
    :param str blob_name: Azure Blob Storage blob name
    :param Union[str, Path] file_path: Path to the DAG file
    :param bool exit_on_failure: Whether to exit on failure, default True
    :rtype: None
    """
    logger = create_logger()
    if isinstance(file_path, str):
        file_path = Path(file_path)
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(file_path.read_bytes(), overwrite=True)
        logger.info(f"{file_path} with {blob_name} uploaded to Azure Blob Storage")
    except Exception as e:
        logger.error(f"Failed to upload DAG to Azure Blob Storage: {e}")
        if exit_on_failure:
            sys.exit(1)


def retrieve_dags_to_upload(path: Union[str, Path], file_extension: str = ".py") -> List[Tuple[Path, str]]:
    """
    Retrieve DAGs to upload to Azure Blob Storage

    :param Union[str, Path] path: Path to the DAGs folder
    :param str file_extension: File extension of the DAGs, default .py
    :return: List of DAGs to upload
    :rtype: List[Tuple[Path, str]]
    """
    if isinstance(path, str):
        path = Path(path)
    dags = path.glob(f"*{file_extension}")
    return [(dag, dag.name) for dag in dags]


def upload_dags_to_blob_storage(
    path: str = "airflow/dags/",
    connection_string: Optional[str] = None,
    container_name: Optional[str] = None,
    exit_on_failure: bool = True,
) -> None:
    """Upload DAGs to Azure Blob Storage

    :param str path: Path to the DAGs folder, default airflow/dags/
    :param Optional[str] connection_string: Azure Blob Storage connection string
    :param Optional[str] container_name: Azure Blob Storage container name
    :param bool exit_on_failure: Whether to exit on failure, default True
    :rtype: None
    """
    logger = create_logger()
    if connection_string is None:
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if container_name is None:
        container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
    if connection_string is None or container_name is None:
        logger.error("Please provide the connection string and container name for Azure Blob Storage.")
        if exit_on_failure:
            sys.exit(1)
    dags = retrieve_dags_to_upload(path)
    for dag, blob_name in dags:
        upload_dag_to_blob_storage(
            connection_string=connection_string,
            container_name=container_name,
            blob_name=blob_name,
            file_path=dag,
            exit_on_failure=exit_on_failure,
        )


def main():
    """Entrypoint for uploading DAGs to Azure Blob Storage."""
    logger = create_logger()
    if len(sys.argv) == 2:
        connection_string = sys.argv[1]
        container_name = sys.argv[2]
    else:
        connection_string = os.environ.get("ADS_CONN_STRING")
        container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "dags")
    if connection_string is None or container_name is None:
        logger.error("Please provide the connection string and container name for Azure Blob Storage.")
        if connection_string is None:
            logger.error("Connection string not provided.")
        if container_name is None:
            logger.error("Container name not provided.")
        sys.exit(1)
    upload_dags_to_blob_storage(
        connection_string=connection_string,
        container_name=container_name,
        exit_on_failure=False,
    )


if __name__ == "__main__":
    main()

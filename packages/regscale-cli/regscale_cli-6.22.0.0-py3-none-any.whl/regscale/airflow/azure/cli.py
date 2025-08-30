"""Provide a CLI for uploading DAGs to Azure Blob Storage."""

import os
import sys
import click

from regscale.airflow.azure.upload_dags import (
    upload_dag_to_blob_storage,
    upload_dags_to_blob_storage,
)


@click.group(name="dags")
def cli():
    """Upload DAGs or files to Azure Blob Storage."""
    pass


@cli.command()
@click.option(
    "--file",
    "-f",
    "file_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to the DAG file to upload.",
)
@click.option(
    "--conn-string",
    "-c",
    "connection_string",
    default=os.getenv("AZURE_STORAGE_CONNECTION_STRING", None),
    help="Azure Blob Storage connection string.",
)
@click.option(
    "--container",
    "-n",
    "container_name",
    default=os.getenv("AZURE_STORAGE_CONTAINER_NAME", "dags"),
    help="Azure Blob Storage container name.",
)
def upload_dag(file_path: str, connection_string: str, container_name: str) -> None:
    """Upload a single DAG to Azure Blob Storage."""
    if connection_string is None:
        click.echo("You can set the connection string with the AZURE_STORAGE_CONNECTION_STRING environment variable.")
    if container_name is None:
        click.echo("You can set the container name with the AZURE_STORAGE_CONTAINER_NAME environment variable.")
    if connection_string is None or container_name is None:
        click.echo("Please provide the connection string and container name for Azure Blob Storage.")
        sys.exit(1)
    upload_dag_to_blob_storage(
        connection_string=connection_string,
        container_name=container_name,
        blob_name=file_path,
        file_path=file_path,
    )


@cli.command()
@click.option("--path", "-p", "path", default="airflow/dags/", help="Path to the DAGs folder.")
@click.option(
    "--conn-string",
    "-c",
    "connection_string",
    default=os.getenv("AZURE_STORAGE_CONNECTION_STRING", None),
    help="Azure Blob Storage connection string.",
)
@click.option(
    "--container",
    "-n",
    "container_name",
    default=os.getenv("AZURE_STORAGE_CONTAINER_NAME", "dags"),
    help="Azure Blob Storage container name.",
)
def upload_dags(path: str, connection_string: str, container_name: str) -> None:
    """Upload DAGs to Azure Blob Storage."""
    if connection_string is None or container_name is None:
        click.echo("Please provide the connection string and container name for Azure Blob Storage.")
    if connection_string is None:
        click.echo("You can set the connection string with the AZURE_STORAGE_CONNECTION_STRING environment variable.")
    if container_name is None:
        click.echo("You can set the container name with the AZURE_STORAGE_CONTAINER_NAME environment variable.")
    if connection_string is None or container_name is None:
        sys.exit(1)
    upload_dags_to_blob_storage(
        path=path,
        connection_string=connection_string,
        container_name=container_name,
    )

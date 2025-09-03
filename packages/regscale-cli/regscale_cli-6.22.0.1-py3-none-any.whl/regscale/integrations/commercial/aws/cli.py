"""AWS CLI integration module."""

import json
import logging
import os
from datetime import datetime
from typing import Optional

import click

from regscale.models.integration_models.flat_file_importer import FlatFileImporter

logger = logging.getLogger("regscale")


@click.group(name="aws")
def awsv2():
    """AWS Integrations."""
    pass


@awsv2.command(name="sync_assets")
@click.option(
    "--region",
    type=str,
    default=os.environ.get("AWS_REGION", "us-east-1"),
    help="AWS region to collect inventory from",
)
@click.option(
    "--regscale_id",
    "--id",
    type=click.INT,
    help="RegScale will create and update assets as children of this record.",
    required=True,
)
@click.option(
    "--aws_access_key_id",
    type=str,
    required=False,
    help="AWS access key ID",
    envvar="AWS_ACCESS_KEY_ID",
)
@click.option(
    "--aws_secret_access_key",
    type=str,
    required=False,
    help="AWS secret access key",
    default=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
@click.option(
    "--aws_session_token",
    type=click.STRING,
    required=False,
    help="AWS Session ID",
    default=os.environ.get("AWS_SESSION_TOKEN"),
)
def sync_assets(
    region: str,
    regscale_id: int,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
) -> None:
    """
    Sync AWS resources to RegScale assets.

    This command collects AWS resources and creates/updates corresponding assets in RegScale:
    - EC2 instances
    - S3 buckets
    - RDS instances
    - Lambda functions
    - DynamoDB tables
    - VPCs and networking resources
    - Container resources
    - And more...
    """
    try:
        logger.info("Starting AWS asset sync to RegScale...")
        from .scanner import AWSInventoryIntegration

        scanner = AWSInventoryIntegration(plan_id=regscale_id)
        scanner.sync_assets(
            plan_id=regscale_id,
            region=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        logger.info("AWS asset sync completed successfully.")
    except Exception as e:
        logger.error(f"Error syncing AWS assets: {e}", exc_info=True)
        raise click.ClickException(str(e))


@awsv2.group()
def inventory():
    """AWS resource inventory commands."""
    pass


@inventory.command(name="collect")
@click.option(
    "--region",
    type=str,
    default=os.getenv("AWS_REGION", "us-east-1"),
    help="AWS region to collect inventory from. Default is us-east-1.",
)
@click.option(
    "--aws_access_key_id",
    type=str,
    required=False,
    help="AWS access key ID",
    envvar="AWS_ACCESS_KEY_ID",
)
@click.option(
    "--aws_secret_access_key",
    type=str,
    required=False,
    help="AWS secret access key",
    envvar="AWS_SECRET_ACCESS_KEY",
)
@click.option(
    "--aws_session_token",
    type=click.STRING,
    required=False,
    help="AWS Session ID",
    default=os.environ.get("AWS_SESSION_TOKEN"),
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    help="Output file path (JSON format)",
    required=False,
)
def collect_inventory(
    region: str,
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
    aws_session_token: Optional[str],
    output: Optional[str],
) -> None:
    """
    Collect AWS resource inventory.

    This command collects information about various AWS resources including:
    - EC2 instances
    - S3 buckets
    - RDS instances
    - Lambda functions
    - And more...

    The inventory can be displayed to stdout or saved to a JSON file.
    """
    try:
        from .inventory import collect_all_inventory
        from regscale.models import DateTimeEncoder

        logger.info("Collecting AWS inventory...")
        aws_inventory = collect_all_inventory(
            region=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        logger.info(
            "AWS inventory collected successfully. Received %s resource(s).",
            sum(len(resources) for resources in aws_inventory.values()),
        )

        if output:
            with open(output, "w") as f:
                json.dump(aws_inventory, f, indent=2, cls=DateTimeEncoder)
            logger.info(f"Inventory saved to {output}")
        else:
            click.echo(json.dumps(aws_inventory, indent=2, cls=DateTimeEncoder))

    except Exception as e:
        logger.error(f"Error collecting AWS inventory: {e}")
        raise click.ClickException(str(e))


@awsv2.group(help="Sync AWS Inspector Scans to RegScale.")
def inspector():
    """Sync AWS Inspector scans."""


@inspector.command(name="import_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing AWS Inspector files to process to RegScale.",
    prompt="File path for AWS Inspector files (CSV or JSON)",
    import_name="aws_inspector",
)
def import_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: click.Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Import AWS Inspector scans to a System Security Plan in RegScale as assets and vulnerabilities.
    """
    import_aws_scans(
        folder_path=folder_path,
        regscale_ssp_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def import_aws_scans(
    folder_path: os.PathLike[str],
    regscale_ssp_id: int,
    mappings_path: click.Path,
    scan_date: datetime,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    disable_mapping: Optional[bool] = False,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Function to import AWS Inspector scans to RegScale as assets and vulnerabilities

    :param os.PathLike[str] folder_path: Path to the folder containing AWS Inspector files
    :param int regscale_ssp_id: RegScale System Security Plan ID
    :param datetime.date scan_date: Date of the scan
    :param click.Path mappings_path: Path to the header mapping file
    :param str s3_bucket: The S3 bucket to download the files from
    :param str s3_prefix: The S3 prefix to download the files from
    :param str aws_profile: The AWS profile to use for S3 access
    :param bool disable_mapping: Disable header mapping
    :param bool upload_file: Upload the file to RegScale after processing, defaults to True
    :rtype: None
    """
    from regscale.models.integration_models.amazon_models.inspector_scan import InspectorScan

    FlatFileImporter.import_files(
        import_type=InspectorScan,
        import_name="AWS Inspector",
        file_types=[".csv", ".json"],
        folder_path=folder_path,
        object_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


@awsv2.command(name="sync_findings")
@click.option(
    "--region",
    type=str,
    default=os.environ.get("AWS_REGION", "us-east-1"),
    help="AWS region to collect findings from",
)
@click.option(
    "--regscale_id",
    "--id",
    type=click.INT,
    help="RegScale will create and update findings as children of this record.",
    required=True,
)
@click.option(
    "--aws_access_key_id",
    type=str,
    required=False,
    help="AWS access key ID",
    envvar="AWS_ACCESS_KEY_ID",
)
@click.option(
    "--aws_secret_access_key",
    type=str,
    required=False,
    help="AWS secret access key",
    default=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
@click.option(
    "--aws_session_token",
    type=click.STRING,
    required=False,
    help="AWS Session ID",
    default=os.environ.get("AWS_SESSION_TOKEN"),
)
def sync_findings(
    region: str,
    regscale_id: int,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
) -> None:
    """
    Sync AWS Security Hub findings to RegScale.

    This command fetches findings from AWS Security Hub and creates/updates
    corresponding issues in RegScale.
    """
    try:
        logger.info("Starting AWS Security Hub findings sync to RegScale...")
        from .scanner import AWSInventoryIntegration

        scanner = AWSInventoryIntegration(plan_id=regscale_id)
        findings_processed = scanner.sync_findings(
            plan_id=regscale_id,
            region=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        logger.info(f"AWS Security Hub findings sync completed successfully. Processed {findings_processed} findings.")
    except Exception as e:
        logger.error(f"Error syncing AWS Security Hub findings: {e}", exc_info=True)
        raise click.ClickException(str(e))


@awsv2.command(name="sync_findings_and_assets")
@click.option(
    "--region",
    type=str,
    default=os.environ.get("AWS_REGION", "us-east-1"),
    help="AWS region to collect findings and assets from",
)
@click.option(
    "--regscale_id",
    "--id",
    type=click.INT,
    help="RegScale will create and update findings and assets as children of this record.",
    required=True,
)
@click.option(
    "--aws_access_key_id",
    type=str,
    required=False,
    help="AWS access key ID",
    envvar="AWS_ACCESS_KEY_ID",
)
@click.option(
    "--aws_secret_access_key",
    type=str,
    required=False,
    help="AWS secret access key",
    default=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
@click.option(
    "--aws_session_token",
    type=click.STRING,
    required=False,
    help="AWS Session ID",
    default=os.environ.get("AWS_SESSION_TOKEN"),
)
def sync_findings_and_assets(
    region: str,
    regscale_id: int,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
) -> None:
    """
    Sync AWS Security Hub findings and automatically discovered assets to RegScale.

    This command fetches findings from AWS Security Hub, creates/updates corresponding
    issues in RegScale, and also creates assets for the resources referenced in the findings.
    This provides a comprehensive view by creating both the security findings and the
    underlying AWS resources they reference.
    """
    try:
        logger.info("Starting AWS Security Hub findings and assets sync to RegScale...")
        from .scanner import AWSInventoryIntegration

        scanner = AWSInventoryIntegration(plan_id=regscale_id)
        findings_processed, assets_processed = scanner.sync_findings_and_assets(
            plan_id=regscale_id,
            region=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        logger.info(
            f"AWS Security Hub sync completed successfully. "
            f"Processed {findings_processed} findings and {assets_processed} assets."
        )
    except Exception as e:
        logger.error(f"Error syncing AWS Security Hub findings and assets: {e}", exc_info=True)
        raise click.ClickException(str(e))


@awsv2.group()
def findings():
    """AWS Security Hub findings commands."""
    pass


@findings.command(name="collect")
@click.option(
    "--region",
    type=str,
    default=os.getenv("AWS_REGION", "us-east-1"),
    help="AWS region to collect findings from. Default is us-east-1.",
)
@click.option(
    "--aws_access_key_id",
    type=str,
    required=False,
    help="AWS access key ID",
    envvar="AWS_ACCESS_KEY_ID",
)
@click.option(
    "--aws_secret_access_key",
    type=str,
    required=False,
    help="AWS secret access key",
    envvar="AWS_SECRET_ACCESS_KEY",
)
@click.option(
    "--aws_session_token",
    type=click.STRING,
    required=False,
    help="AWS Session ID",
    default=os.environ.get("AWS_SESSION_TOKEN"),
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    help="Output file path (JSON format). Default: artifacts/aws/findings.json",
    required=False,
)
def collect_findings(
    region: str,
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
    aws_session_token: Optional[str],
    output: Optional[str],
) -> None:
    """
    Collect AWS Security Hub findings.

    This command fetches findings from AWS Security Hub and displays them to stdout
    or saves them to a JSON file. The findings include security issues, compliance
    violations, and other security-related information from AWS Security Hub.

    If no output file is specified, findings will be saved to artifacts/aws/findings.json
    by default. Use --output - to display to stdout instead.
    """
    try:
        import boto3
        from regscale.integrations.commercial.amazon.common import fetch_aws_findings
        from regscale.models import DateTimeEncoder

        logger.info("Collecting AWS Security Hub findings...")

        # Create AWS session
        session = boto3.Session(
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        client = session.client("securityhub")

        # Fetch findings
        findings = fetch_aws_findings(aws_client=client)

        logger.info(f"AWS Security Hub findings collected successfully. Found {len(findings)} finding(s).")

        # Default output path
        if output is None:
            output = os.path.join("artifacts", "aws", "findings.json")

        if output == "-":
            # Output to stdout
            click.echo(json.dumps(findings, indent=2, cls=DateTimeEncoder))
        else:
            # Save to file
            # Ensure the artifacts directory exists
            os.makedirs(os.path.dirname(output), exist_ok=True)

            with open(output, "w", encoding="utf-8") as f:
                json.dump(findings, f, indent=2, cls=DateTimeEncoder)
            logger.info(f"Findings saved to {output}")

    except Exception as e:
        logger.error(f"Error collecting AWS Security Hub findings: {e}", exc_info=True)
        raise click.ClickException(str(e))

"""
Utility functions for working with files and folders.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Union, List, Iterator, Optional


class S3FileDownloadError(Exception):
    """
    Exception raised when an error occurs during S3 file downloadß
    """

    pass


def is_s3_path(path: Union[str, Path]) -> bool:
    """
    Check if the given path is an S3 URI.

    :param Union[str, Path] path: The path to check
    :return: True if the path is an S3 URI, False otherwise
    :rtype: bool
    """
    return isinstance(path, str) and path.startswith("s3://")


def read_file(file_path: Union[str, Path]) -> str:
    """
    Read a file from local filesystem or S3.

    :param Union[str, Path] file_path: Path to the file or S3 URI
    :return: Content of the file
    :rtype: str
    """
    import smart_open  # type: ignore # Optimize import performance

    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

    for encoding in encodings:
        try:
            with smart_open.open(str(file_path), "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    # Fallback to utf-8 with error replacement
    with smart_open.open(str(file_path), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def find_files(path: Union[str, Path], pattern: str) -> List[Union[Path, str]]:
    """
    Find all files matching the pattern in the given path, including S3.

    :param Union[str, Path] path: Path to a file, a folder, or an S3 URI
    :param str pattern: File pattern to match (e.g., "*.nessus")
    :return: List of Path objects for matching files or S3 URIs
    :rtype: List[Union[Path, str]]
    """
    import boto3  # type: ignore # Optimize import performance

    if is_s3_path(path):
        s3_parts = path[5:].split("/", 1)
        bucket = s3_parts[0]
        prefix = s3_parts[1] if len(s3_parts) > 1 else ""

        s3 = boto3.client("s3")
        paginator = s3.get_paginator("list_objects_v2")

        files: List[Union[Path, str]] = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                if obj["Key"].endswith(pattern.lstrip("*")):
                    files.append(f"s3://{bucket}/{obj['Key']}")
        return files

    file_path = Path(path)
    if file_path.is_file():
        return [file_path] if file_path.match(pattern) else []
    return list(file_path.glob(pattern))


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """
    Move a file from src to dst. Works with local files and S3.

    :param Union[str, Path] src: Source file path or S3 URI
    :param Union[str, Path] dst: Destination file path or S3 URI
    """
    import smart_open  # type: ignore # Optimize import performance

    if is_s3_path(src):
        import boto3  # type: ignore # Optimize import performance

        # S3 to S3 move
        if is_s3_path(dst):
            s3 = boto3.client("s3")
            src_parts = src[5:].split("/", 1)
            dst_parts = dst[5:].split("/", 1)
            s3.copy_object(
                CopySource={"Bucket": src_parts[0], "Key": src_parts[1]}, Bucket=dst_parts[0], Key=dst_parts[1]
            )
            s3.delete_object(Bucket=src_parts[0], Key=src_parts[1])
        else:
            # S3 to local
            with smart_open.open(src, "rb") as s_file, smart_open.open(dst, "wb") as d_file:
                d_file.write(s_file.read())
            s3 = boto3.client("s3")
            src_parts = src[5:].split("/", 1)
            s3.delete_object(Bucket=src_parts[0], Key=src_parts[1])
    else:
        # Local to local or local to S3
        with smart_open.open(src, "rb") as s_file, smart_open.open(dst, "wb") as d_file:
            d_file.write(s_file.read())
        if not isinstance(dst, str) or not dst.startswith("s3://"):
            os.remove(src)


def iterate_files(file_collection: List[Union[Path, str]]) -> Iterator[Union[Path, str]]:
    """
    Iterate over a collection of files, yielding each file path.

    :param List[Union[Path, str]] file_collection: List of file paths or S3 URIs
    :yield: Each file path or S3 URI
    :rtype: Iterator[Union[Path, str]]
    """
    for file in file_collection:
        yield file


def get_processed_file_path(file_path: Union[str, Path], processed_folder: str = "processed") -> Union[str, Path]:
    """
    Generate a path for the processed file, handling both local and S3 paths.

    :param Union[str, Path] file_path: Original file path or S3 URI
    :param str processed_folder: Name of the folder for processed files (default: "processed")
    :return: Path or S3 URI for the processed file
    :rtype: Union[str, Path]
    """
    if is_s3_path(file_path):
        s3_parts = file_path[5:].split("/")  # type: ignore  # is_s3_path ensures string
        bucket = s3_parts[0]
        key = "/".join(s3_parts[1:])
        new_key = f"processed/{os.path.basename(key)}"
        return f"s3://{bucket}/{new_key}"
    else:
        file_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d-%I%M%S%p")
        new_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}".replace(" ", "_")
        new_path = file_path.parent / processed_folder / new_filename
        os.makedirs(new_path.parent, exist_ok=True)
        return new_path


def get_files_by_folder(
    import_folder: Union[str, Path],
    exclude_non_scan_files: bool,
    file_excludes: Optional[list[str]] = None,
    directory_excludes: Optional[list[str]] = None,
) -> List[str]:
    """
    Retrieves a list of file paths from a specified folder, excluding empty files or files that match the excludes list.

    :param Union[str, Path] import_folder: The path to the folder from which to retrieve file paths.
    :param bool exclude_non_scan_files: exclude files that are not scan files
    :param Optional[List[str]] file_excludes: List of file extensions to exclude from the list of files
    :param Optional[List[str]] directory_excludes: List of directories to exclude from the list of files
    :return: A list of file paths for all non-empty files in the specified folder and subsequent subfolders.
    :rtype: List[str]
    """
    if file_excludes is None:
        file_excludes = []
    if directory_excludes is None:
        directory_excludes = []
    file_path_list = []
    if not os.path.isdir(import_folder):
        from regscale.core.app.logz import create_logger

        logger = create_logger()
        logger.error(f"Folder '{import_folder}' does not exist.")
        return file_path_list
    for root, dir, files in os.walk(import_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if any(exclude_str in file_path for exclude_str in directory_excludes):
                continue
            if any(exclude_str in file for exclude_str in file_excludes) and exclude_non_scan_files:
                continue
            if os.path.getsize(file_path) == 0:
                continue
            file_path_list.append(os.path.join(root, file))
    return file_path_list


def download_from_s3(bucket: str, prefix: str, local_path: Union[str, os.PathLike], aws_profile: str) -> None:
    """
    Downloads files from an S3 bucket to a local directory.

    :param str bucket: Name of the S3 bucket
    :param str prefix: Prefix (folder path) within the bucket
    :param Union[str, PathLike] local_path: Local directory to download files to
    :param str aws_profile: AWS profile to use for S3 access
    :rtype: None
    """
    import boto3
    import logging
    from botocore.exceptions import ClientError

    logger = logging.getLogger(__name__)

    session = boto3.Session(profile_name=aws_profile)
    s3_client = session.client("s3")

    try:
        # Create local directory if it doesn't exist
        os.makedirs(local_path, exist_ok=True)

        # List objects in bucket with given prefix
        paginator = s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if "Contents" not in page:
                continue

            for obj in page["Contents"]:
                # Skip if object is a directory (ends with /)
                if obj["Key"].endswith("/"):
                    continue

                # Create the full local path, preserving directory structure
                relative_path = obj["Key"]
                if prefix:
                    # Remove the prefix from the key to get the relative path
                    relative_path = relative_path[len(prefix) :].lstrip("/")

                local_file_path = os.path.join(local_path, relative_path)

                # Create the directory structure if it doesn't exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                logger.info(f"Downloading {obj['Key']} to {local_file_path}")
                s3_client.download_file(bucket, obj["Key"], local_file_path)

    except ClientError as e:
        logger.error(f"Error downloading from S3: {str(e)}")
        raise S3FileDownloadError(f"Failed to download files from S3: {str(e)}")

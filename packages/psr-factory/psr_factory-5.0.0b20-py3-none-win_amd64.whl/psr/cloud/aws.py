import os
import tempfile
import zipfile
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


def _get_region(url):
    """Extract the region from the S3 URL."""
    if url:
        parts = url.split(".")
        return parts[0]
    return None


def upload_file_to_s3(
    s3_client, bucket_name, file_path, object_name=None, extra_args=None
):
    """Upload a file to an S3 bucket using a provided S3 client.

    :param s3_client: Initialized S3 client.
    :param bucket_name: Name of the S3 bucket.
    :param file_path: Path to the file to upload.
    :param object_name: S3 object name. If not specified, file_path's basename is used.
    :param extra_args: A dictionary of extra arguments to pass to S3's upload_file.
    :return: True if file was uploaded, else False.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs=extra_args)
        return True
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False


def upload_case_to_s3(
    files: List[str],
    repository_id: str,
    cluster_name: str,
    checksums: Optional[Dict[str, str]] = None,
    access: Optional[str] = None,
    secret: Optional[str] = None,
    session_token: Optional[str] = None,
    bucket_name: Optional[str] = None,
    url: Optional[str] = None,
    zip_compress: bool = False,
    compress_zip_name: str = None,
):
    """Upload files to an S3 bucket."""

    region = _get_region(url)

    if not region or not access or not secret or not session_token or not bucket_name:
        raise ValueError("Unable to set up AWS connection.")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        aws_session_token=session_token,
        region_name=region,
    )

    # Base metadata, common for both zip and individual files
    base_metadata: Dict[str, str] = {
        "upload": str(True).lower(),
        "user-agent": "aws-fsx-lustre",
        "file-owner": "537",
        "file-group": "500",
        "file-permissions": "100777",
    }

    if zip_compress and not compress_zip_name:
        compress_zip_name = str(repository_id)

    if zip_compress:
        # Create a temporary zip file
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip_file:
            zip_path = tmp_zip_file.name
            tmp_zip_file.close()  # Close the file handle so zipfile can open it

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    # Add file to zip, using only the basename inside the zip
                    zipf.write(file_path, arcname=os.path.basename(file_path))

            # Construct object name for the zip file
            object_name = f"{repository_id}/uploaded/{compress_zip_name}.zip"

            # For zip files, we use the base metadata without a specific checksum
            # (as checksums are per-file in the original design)
            extra_args = {
                "Metadata": base_metadata.copy()
            }  # Use a copy to avoid modifying base_metadata

            if not upload_file_to_s3(
                s3_client, bucket_name, zip_path, object_name, extra_args=extra_args
            ):
                raise ValueError(
                    f"Failed to upload zip file {zip_path} to S3 bucket {bucket_name}."
                )

        finally:
            # Clean up the temporary zip file
            if os.path.exists(zip_path):
                os.unlink(zip_path)

    else:
        # Original logic: upload files individually
        for file_path in files:
            file_basename = os.path.basename(file_path)
            object_name = f"{repository_id}/uploaded/{file_basename}"

            current_file_metadata = base_metadata.copy()
            if checksums:
                current_file_metadata["checksum"] = checksums.get(file_basename, "")

            extra_args = {"Metadata": current_file_metadata}

            if not upload_file_to_s3(
                s3_client, bucket_name, file_path, object_name, extra_args=extra_args
            ):
                raise ValueError(
                    f"Failed to upload file {file_path} to S3 bucket {bucket_name}."
                )

    # Always upload .metadata files if the source 'files' list is provided
    if files:
        # Assuming all files in the 'files' list share the same parent directory,
        # which is the case data directory.
        data_directory = os.path.dirname(files[0])
        metadata_dir_local_path = os.path.join(data_directory, ".metadata")

        if os.path.isdir(metadata_dir_local_path):
            # Iterate through the original list of files to find corresponding metadata files
            for original_file_path in files:
                original_file_basename = os.path.basename(original_file_path)
                local_metadata_file_path = os.path.join(
                    metadata_dir_local_path, original_file_basename
                )

                if os.path.isfile(local_metadata_file_path):
                    # S3 object name for the metadata file (e.g., repository_id/.metadata/original_file_basename)
                    s3_metadata_object_name = (
                        f"{repository_id}/.metadata/{original_file_basename}"
                    )
                    extra_args = {"Metadata": base_metadata.copy()}
                    if not upload_file_to_s3(
                        s3_client,
                        bucket_name,
                        local_metadata_file_path,
                        s3_metadata_object_name,
                        extra_args=extra_args,
                    ):
                        raise ValueError(
                            f"Failed to upload metadata file {local_metadata_file_path} to S3 bucket {bucket_name}."
                        )


def _download_s3_object(
    s3_client, bucket_name: str, s3_object_key: str, local_file_path: str
) -> bool:
    """
    Downloads a single object from S3 to a local file path.

    :param s3_client: Initialized S3 client.
    :param bucket_name: Name of the S3 bucket.
    :param s3_object_key: The key of the object in S3.
    :param local_file_path: The local path where the file should be saved.
    :return: True if download was successful, False otherwise.
    """

    try:
        s3_client.download_file(bucket_name, s3_object_key, local_file_path)
        return True
    except ClientError as e:
        print(f"ERROR: Failed to download {s3_object_key} from S3: {e}")
        return False


def download_case_from_s3(
    repository_id: str,
    cluster_name: str,  # Kept for consistency with caller, though not used directly in S3 ops
    access: str,
    secret: str,
    session_token: str,
    bucket_name: str,
    url: str,  # S3 endpoint URL, used by _get_region
    output_path: str,
    file_list: List[str],
) -> List[str]:
    """
    Downloads files from an S3 bucket for a given case repository.

    It iterates through the provided `file_list`, downloads each specified file
    from the S3 path `{repository_id}/{file_in_list}`, preserving its relative path
    under `output_path`. It then checks if each downloaded file is gzipped,
    decompresses it if necessary, and returns a list of basenames of the
    final downloaded (and potentially decompressed) files.

    :param repository_id: The ID of the repository in S3.
    :param cluster_name: Name of the cluster (for context, not used in S3 calls).
    :param access: AWS access key ID.
    :param secret: AWS secret access key.
    :param session_token: AWS session token.
    :param bucket_name: Name of the S3 bucket.
    :param url: S3 service URL (used to determine region via _get_region).
    :param output_path: Local directory where files will be downloaded.
    :param file_list: A list of file names (basenames) to be downloaded.
    :return: A list of basenames of the downloaded (and decompressed) files.
    :raises ValueError: If S3 connection parameters are missing or filter is invalid.
    :raises RuntimeError: If S3 operations fail.
    """
    region = _get_region(url)
    if not all([region, access, secret, session_token, bucket_name]):
        # TODO: Replace print with proper logging
        print(
            "ERROR: Missing S3 connection parameters (region, access, secret, token, or bucket name)."
        )
        raise ValueError("Missing S3 connection parameters.")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        aws_session_token=session_token,
        region_name=region,
    )

    downloaded_files: List[str] = []

    try:
        for file_name in file_list:
            # Construct the full S3 object key
            s3_object_key = f"{repository_id}/{file_name}"

            local_file_path = os.path.join(output_path, file_name)
            if _download_s3_object(
                s3_client, bucket_name, s3_object_key, local_file_path
            ):
                downloaded_files.append(os.path.basename(local_file_path))

    except ClientError as e:
        print(f"ERROR: S3 ClientError during download: {e}")
        raise RuntimeError(f"Failed to download files from S3: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during download: {e}")
        raise RuntimeError(f"An unexpected error occurred during S3 download: {e}")

    return downloaded_files

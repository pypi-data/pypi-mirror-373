# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import boto3
from loguru import logger

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

S3_URI_SCHEME = "s3://"
S3_BUCKET_SEPARATOR = "/"
S3_BOTO_CLIENT = "s3"

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def parse_s3_url(s3_url: str) -> tuple[str, str]:
    """
    :param s3_url: S3 URL to parse and extract the bucket and blob names from.
    :return: Tuple of:
        - Bucket name.
        - Blob name.
    """

    if s3_url.startswith(S3_URI_SCHEME):
        s3_url = s3_url.replace(S3_URI_SCHEME, "")

    parts = s3_url.split(S3_BUCKET_SEPARATOR, 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ""

    return bucket, key


def download_s3_file(s3_url: str, local_path: str) -> None:
    """
    :param s3_url: S3 URL to download data from.
    :param local_path: Path to save the contents of the download to.
    """

    bucket, key = parse_s3_url(s3_url)

    s3 = boto3.client(S3_BOTO_CLIENT)

    logger.info(f"Downloading {s3_url} to {local_path}...")
    s3.download_file(bucket, key, local_path)
    logger.success("Done.")

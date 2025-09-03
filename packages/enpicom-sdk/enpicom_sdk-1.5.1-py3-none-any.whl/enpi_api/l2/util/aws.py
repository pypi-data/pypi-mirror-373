"""@private
Nothing in this module is useful for customers to invoke directly, hide it from the docs.
"""

import boto3
from mypy_boto3_s3 import S3Client

from enpi_api.l2.types.file import FederatedCredentials


def get_s3_client(credentials: FederatedCredentials) -> S3Client:
    """Gets a boto3 S3 client initialized with passed federated credentials.

    Args:
        credentials (FederatedCredentials): Temporary credentials used for the upload.

    Returns:
        mypy_boto3_s3.S3Client: Boto3's client used for interraction with S3.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.access_key_secret,
        aws_session_token=credentials.session_token,
    )

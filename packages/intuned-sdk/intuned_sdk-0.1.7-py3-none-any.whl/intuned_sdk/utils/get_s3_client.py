import os

from boto3 import client


def get_s3_client(endpoint_url=None):
    region_name = os.environ.get("S3_REGION") or os.environ.get("INTUNED_S3_REGION")
    aws_access_key_id = os.environ.get("S3_ACCESS_KEY_ID") or os.environ.get(
        "INTUNED_S3_ACCESS_KEY_ID"
    )
    aws_secret_access_key = os.environ.get("S3_SECRET_ACCESS_KEY") or os.environ.get(
        "INTUNED_S3_SECRET_ACCESS_KEY"
    )

    return client(
        "s3",
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=endpoint_url,
    )

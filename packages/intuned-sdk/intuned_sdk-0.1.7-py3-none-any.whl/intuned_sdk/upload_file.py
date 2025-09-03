import logging
import os
import re
import uuid
from enum import Enum
from typing import Dict
from typing import Optional
from typing import TypedDict
from typing import Union

from dataclasses import dataclass
from botocore.exceptions import NoCredentialsError
from playwright.async_api import Download
from pydantic import BaseModel
from pydantic import Field

from .utils.get_mode import is_generate_code_mode
from .utils.get_s3_client import get_s3_client

logger = logging.getLogger(__name__)


@dataclass
class UploadedFile:
    file_name: str
    bucket: str
    region: str
    endpoint: str | None
    suggested_file_name: str


def sanitize_key(key):
    """
    Sanitize a key string by replacing non-alphanumeric characters with underscores
    and consolidating multiple underscores into single underscores.
    Args:
        key (str): The input string to sanitize
    Returns:
        str: Sanitized string
    """
    # Replace any non-alphanumeric chars (except .-_/) with underscore
    result = re.sub(r"[^a-zA-Z0-9.\-_/]", "_", key)
    # Replace multiple underscores with single underscore
    result = re.sub(r"_{2,}", "_", result)
    return result


class AttachmentType(str, Enum):
    DOCUMENT = "document"


class Attachment(BaseModel):
    file_name: str
    bucket: str
    region: str
    endpoint: Optional[str] = None
    suggested_file_name: str
    file_type: AttachmentType = Field(default=AttachmentType.DOCUMENT)

    def __json__(self):
        return self.model_dump()

    def to_dict(self) -> Dict[str, str]:
        return {
            "file_name": self.file_name,
            "bucket": self.bucket,
            "region": self.region,
            "endpoint": self.endpoint,  # type: ignore
            "suggested_file_name": self.suggested_file_name,
            "file_type": self.file_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Attachment":
        return cls(**data)  # type: ignore

    def get_signed_url(self, expiration: int = 3600 * 24 * 5):
        if is_generate_code_mode():
            return "https://not.real.com"
        s3_client = get_s3_client()

        response = s3_client.generate_presigned_url(  # type: ignore
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": self.file_name},
            ExpiresIn=expiration,
            HttpMethod="GET",
        )
        return response

    def get_s3_key(self):
        if self.should_upload_to_r2():
            raise Exception(
                "get_s3_key function is not supported when using a custom s3 endpoint"
            )

        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{self.file_name}"

    def get_file_path(self):
        return self.file_name

    def should_upload_to_r2(self):
        if isinstance(self.endpoint, str) and self.endpoint == "":
            return False
        return True


class UploadFileToS3Configs(TypedDict):
    endpoint: Optional[str]
    fileNameOverride: Optional[str]


FileType = Union[Download, str, bytes]


async def upload_file_to_s3(
    file: FileType,
    fileNameOverride: Optional[str] = None,
) -> Attachment:
    bucket_name = os.environ.get("S3_BUCKET") or os.environ.get("INTUNED_S3_BUCKET")
    region = os.environ.get("S3_REGION") or os.environ.get("INTUNED_S3_REGION")
    endpoint = os.environ.get("R2_ENDPOINT") or os.environ.get("INTUNED_R2_ENDPOINT")

    is_downloaded_file = isinstance(file, Download)
    if is_generate_code_mode():
        logger.info("Uploaded file successfully")
        if is_downloaded_file:
            await file.cancel()
            return Attachment(
                file_name=f"{str(uuid.uuid4())}/{file.suggested_filename}",
                bucket="testing_bucket",
                region="testing_region",
                endpoint=endpoint,
                suggested_file_name=file.suggested_filename,
                file_type=AttachmentType.DOCUMENT,
            )
        else:
            image_name = file.split("/")[-1]  # type: ignore
            return Attachment(
                file_name=f"{str(uuid.uuid4())}/{image_name}",
                bucket="testing_bucket",
                region="testing_region",
                endpoint=endpoint,
                suggested_file_name=image_name,  # type: ignore
                file_type=AttachmentType.DOCUMENT,
            )

    if region is None or bucket_name is None:
        raise ValueError("S3 credentials not available")

    if is_downloaded_file and not await file.path():
        raise ValueError("File path not found")

    s3_client = get_s3_client(endpoint)

    file_body = await get_file_body(file)

    suggested_file_name = file.suggested_filename if is_downloaded_file else None
    if isinstance(file, str):
        suggested_file_name = file.split("/")[-1]
    logger.info(f"suggested_file_name {suggested_file_name}")
    file_name = (
        fileNameOverride
        if fileNameOverride is not None
        else suggested_file_name or str(uuid.uuid4())
    )

    cleaned_file_name = sanitize_key(file_name)
    key = f"{uuid.uuid4()}/{cleaned_file_name}"
    try:
        response = s3_client.put_object(  # type: ignore
            Bucket=bucket_name,
            Key=key,
            Body=file_body,
        )

    except NoCredentialsError:
        raise Exception("Credentials not available")  # noqa: B904
    finally:
        if isinstance(file, Download):
            await file.delete()
        if isinstance(file, str):
            os.remove(file)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        if not suggested_file_name:
            suggested_file_name = file_name
        return Attachment(
            file_name=key,
            bucket=bucket_name,
            region=region,
            endpoint=endpoint,
            suggested_file_name=suggested_file_name,
            file_type=AttachmentType.DOCUMENT,
        )
    else:
        raise Exception("Error uploading file")


async def get_file_body(file: FileType):
    if isinstance(file, Download):
        file_path = await file.path()
        if not file_path:
            raise ValueError("Downloaded file path not found")
        with open(file_path, "rb") as f:
            return f.read()
    elif isinstance(file, str):
        with open(file, "rb") as f:
            return f.read()
    elif isinstance(file, bytes):
        return file
    else:
        raise ValueError("Invalid file type")

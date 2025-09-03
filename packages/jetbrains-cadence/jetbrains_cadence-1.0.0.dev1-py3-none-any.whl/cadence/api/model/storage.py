from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from cadence.api.model.StorageKey import StorageKey
from cadence.api.model.StorageType import StorageType

DEFAULT_STORAGE_NAME = "Cadence Storage"


class Storage(BaseModel):
    name: str
    access_key_id: Optional[str] = Field(alias="accessKeyId", default=None)
    secret_access_key: Optional[str] = Field(alias="secretAccessKey", default=None)
    profile: Optional[str] = None
    session_token: Optional[str] = Field(alias="sessionToken", default=None)
    bucket: str
    endpoint_url: Optional[str] = Field(alias="endpointUrl", default=None)
    type: StorageType = StorageType.CUSTOM

    @property
    def key(self):
        return StorageKey(name=self.name, type=self.type)


def get_masked(storage: Storage) -> Storage:
    return storage.model_copy(update={"secret_access_key": "***", "session_token": "***"})


def _generate_unique_timestamp() -> str:
    date_formatter = "%Y-%m-%dT%H-%M-%SZ"
    now = datetime.now()
    timestamp = now.strftime(date_formatter)
    uuid_str = str(uuid4())
    unique_timestamp = f"{timestamp}_{uuid_str}"
    return unique_timestamp


class DefaultStorage(Storage):
    name: str = DEFAULT_STORAGE_NAME
    type: StorageType = StorageType.DEFAULT

    prefix: str = Field(exclude=True)
    username: str = Field(exclude=True)
    unique_timestamp: str = Field(exclude=True, default=_generate_unique_timestamp())

    @property
    def base_uri(self) -> str:
        return f"s3://{self.bucket}/{self.prefix.removesuffix('/')}/snapshots/{self.username}/{self.unique_timestamp}"

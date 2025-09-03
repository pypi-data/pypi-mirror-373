from typing import Optional

from pydantic import BaseModel

from cadence.api.model.StorageType import StorageType


class GitConnector(BaseModel):
    uri: str
    branch: Optional[str] = None
    revision: Optional[str] = None
    credentialsId: Optional[str] = None
    type: str = "GIT"


class S3Connector(BaseModel):
    uri: str
    endpointUrl: Optional[str] = None
    profile: Optional[str] = None
    storageType: Optional[StorageType] = None
    credentialsId: Optional[str] = None
    type: str = "S3"


class SSHKeyConnector(BaseModel):
    credentialsId: str
    host: Optional[str] = None
    type: str = "SSH"


class AWSSecretsConnector(BaseModel):
    credentialsId: str
    type: str = "AWS"


Connector = GitConnector | S3Connector | SSHKeyConnector | AWSSecretsConnector

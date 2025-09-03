from typing import Optional

from pydantic import BaseModel

from cadence.api.model.connector import Connector, S3Connector


class GitCredentials(BaseModel):
    user: str
    password: str
    type: str = "GIT"


class S3Credentials(BaseModel):
    accessKeyId: str
    secretAccessKey: str
    sessionToken: Optional[str] = None
    type: str = "S3"


class SSHCredentials(BaseModel):
    keyValue: str
    type: str = "SSH"


class AWSCredentials(BaseModel):
    data: str
    type: str = "AWS"


Credentials = GitCredentials | S3Credentials | SSHCredentials | AWSCredentials


class Input(BaseModel):
    path: str
    connector: Connector


class Mount(BaseModel):
    name: str
    path: str
    connector: S3Connector


class Output(BaseModel):
    path: str
    connector: S3Connector

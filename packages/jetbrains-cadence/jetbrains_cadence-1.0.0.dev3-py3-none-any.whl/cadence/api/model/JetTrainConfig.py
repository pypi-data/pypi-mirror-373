from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from cadence.api.model.StorageType import StorageType
from cadence.api.model.StorageKey import StorageKey


class JetTrainConfig(BaseModel):
    project_name: str
    working_dir: str
    cmd: list[str]
    provisioning: 'ProvisioningConf'
    teamcity: Optional['TeamCityConf'] = None
    env: Optional['EnvConf'] = None
    project_sync: Optional['ProjectSyncConf'] = None
    inputs: list['DataConf'] = Field(default_factory=list)
    outputs: list['DataConf'] = Field(default_factory=list)
    mounts: list['MountConf'] = Field(default_factory=list)
    storages: list['StorageConf'] = Field(default_factory=list)
    description: Optional[str] = None

    class ProvisioningConf(BaseModel):
        gpu_type: Optional[str] = None
        gpu_count: Optional[int] = None

        cpu_count: Optional[int] = None
        ram: Optional[int] = None

    class TeamCityConf(BaseModel):
        url: Optional[str] = None
        build_conf_id: Optional[str] = None
        token: Optional[str] = None

    class EnvConf(BaseModel):
        docker_image: Optional[str] = None
        variables: dict[str, str] = Field(default_factory=dict)
        python: Optional['PythonConf'] = None
        secrets: Optional['SecretsConf'] = None
        aws: Optional['AwsConf'] = None

        class PythonConf(BaseModel):
            pip: Optional['PipConf'] = None
            poetry: Optional['PoetryConf'] = None

            class PipConf(BaseModel):
                version: Optional[str] = None
                requirements_path: str

            class PoetryConf(BaseModel):
                version: Optional[str] = None
                directory: str

        class SecretsConf(BaseModel):
            variables: dict[str, str] = Field(default_factory=dict)
            ssh_keys: list['KeyConf'] = Field(default_factory=list)

            class KeyConf(BaseModel):
                name: str
                path: str
                for_host: Optional[str] = None

        class AwsConf(BaseModel):
            sync_config: Optional[bool] = None  # todo make not optional
            sync_credentials: Optional[bool] = None
            sync_cache: Optional[bool] = None

    class ProjectSyncConf(BaseModel):
        local: Optional['LocalProjectSyncConf'] = None
        git: Optional['GitProjectSyncConf'] = None

        class LocalProjectSyncConf(BaseModel):
            root: str
            storage_name: str
            uri: str
            exclude: list[str] = Field(default_factory=list)
            include: list[str] = Field(default_factory=list)
            sync_back: Optional[bool] = None
            snapshots: Optional[bool] = None
            storage_type: Optional[StorageType] = None

        class GitProjectSyncConf(BaseModel):
            uri: str
            branch: Optional[str] = None
            revision: Optional[str] = None
            user: Optional[str] = None
            password: Optional[str] = None

    class DataConf(BaseModel):
        type: Optional['DataConfType'] = None
        storage_name: str
        uri: str
        path: str
        acceleration: Optional[bool] = None
        storage_type: Optional[StorageType] = None

        class DataConfType(str, Enum):
            INPUT = "INPUT"
            OUTPUT = "OUTPUT"

        @property
        def storage_key(self) -> StorageKey:
            return StorageKey(name=self.storage_name, type=self.storage_type)

        @property
        def source(self) -> str:
            return self.uri if self.type == self.DataConfType.INPUT else self.path

        @property
        def target(self) -> str:
            return self.path if self.type == self.DataConfType.INPUT else self.uri

    class MountConf(BaseModel):
        name: str
        path: str
        uri: str
        type: str
        storage_name: str

    class StorageConf(BaseModel):
        name: str
        storage_type: str
        credentials: 'S3Conf'

        class S3Conf(BaseModel):
            access_key_id: Optional[str] = None
            secret_access_key: Optional[str] = None
            profile: Optional[str] = None
            session_token: Optional[str] = None
            bucket: Optional[str] = None
            endpoint_url: Optional[str] = None
            type: Optional[StorageType] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'JetTrainConfig':
        return cls.model_validate(data)

    def to_dict(self) -> dict:
        return self.model_dump()


def read_config(path: Path) -> JetTrainConfig:
    with path.open('r') as file:
        return JetTrainConfig.from_dict(yaml.safe_load(file))

from typing import Optional

from pydantic import BaseModel, Field

from cadence.api.model.common import Input, Output, Mount, Credentials
from cadence.api.model.environment import Environment
from cadence.api.model.storage import Storage


class ProvisioningRequest(BaseModel):
    gpuCount: Optional[int]
    cpuCount: int
    ram: int


class StartExecutionRequest(BaseModel):
    name: str
    workingDir: str
    cmd: list[str]
    provisioning: 'ProvisioningRequest'
    configName: Optional[str] = None
    description: Optional[str] = None
    env: Optional[Environment] = None
    inputs: list[Input] = Field(default_factory=list)
    outputs: list[Output] = Field(default_factory=list)
    mounts: list[Mount] = Field(default_factory=list)
    metadata: Optional['Metadata'] = None
    credentialsById: dict[str, Credentials] = Field(default_factory=dict)
    parentExecutionId: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    class Metadata(BaseModel):
        s3RootPrefix: Optional[str] = None
        s3RootUri: Optional[str] = None
        localSync: Optional['LocalSync'] = None
        localExecutionId: Optional[str] = None

        class LocalSync(BaseModel):
            root: str
            uri: str
            exclude: list[str] = Field(default_factory=list)
            include: list[str] = Field(default_factory=list)
            storageType: Optional[str] = None

            storage: Storage = Field(exclude=True)


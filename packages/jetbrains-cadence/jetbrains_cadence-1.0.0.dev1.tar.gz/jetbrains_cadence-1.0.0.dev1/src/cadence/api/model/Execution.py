from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from cadence.api.model.License import License
from cadence.api.model.User import User
from cadence.api.model.billing import Credits
from cadence.api.model.common import Input, Mount, Output, Credentials
from cadence.api.model.environment import Environment



class Execution(BaseModel):
    id: int
    name: str
    configName: Optional[str]
    description: Optional[str]
    projectId: str
    status: str
    workingDir: str
    cmd: list[str]
    createdBy: Optional[User] = None
    createdAt: datetime
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    inputs: list[Input] = Field(default_factory=list)
    outputs: list[Output] = Field(default_factory=list)
    mounts: list[Mount] = Field(default_factory=list)
    environment: Optional[Environment] = None
    provisioning: Optional['Provisioning'] = None
    metadata: Optional['Metadata'] = None
    credentialsById: dict[str, Credentials] = Field(default_factory=dict)
    properties: Optional['Properties'] = None
    billingInfo: Optional['BillingInfo'] = None

    class Provisioning(BaseModel):
        id: int
        gpuCount: int
        gpuType: Optional[str]
        cpuCount: int
        ram: int
        price: Optional[Credits]

    class BillingInfo(BaseModel):
        totalCost: Credits
        pricePerHour: Optional[Credits] = None

    class Properties(BaseModel):
        contentRootPath: Optional[str]

    class Metadata(BaseModel):
        s3RootPrefix: Optional[str] = None
        s3RootUri: Optional[str] = None
        localSync: Optional['LocalSync'] = None
        localExecutionId: Optional[str] = None

        class LocalSync(BaseModel):
            root: str
            uri: str
            exclude: Optional[list[str]] = None
            include: Optional[list[str]]= None
            storageType: Optional[str] = None


class ExecutionList(BaseModel):
    offset: int
    count: int
    totalCount: int
    executions: list[Execution]
    license: Optional[License] = None

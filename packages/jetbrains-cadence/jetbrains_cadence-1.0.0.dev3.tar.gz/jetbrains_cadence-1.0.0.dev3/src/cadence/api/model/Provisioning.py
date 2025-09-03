from typing import Optional

from pydantic import BaseModel

from cadence.api.model.billing import Credits


class Provisioning(BaseModel):
    id: int
    gpuCount: int
    gpuType: Optional[str]
    cpuCount: int
    ram: int
    price: Optional[Credits]

class ProvisioningList(BaseModel):
    count: int
    provisioningList: list[Provisioning]
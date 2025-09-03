from enum import Enum

from pydantic import BaseModel

from cadence.api.model.billing import Credits


class LicenseStatus(Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class License(BaseModel):
    licenseId: str
    balance: Credits
    licenseStatus: LicenseStatus

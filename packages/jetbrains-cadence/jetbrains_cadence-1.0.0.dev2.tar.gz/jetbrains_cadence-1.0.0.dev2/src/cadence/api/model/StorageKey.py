from pydantic import BaseModel

from cadence.api.model.StorageType import StorageType


class StorageKey(BaseModel):
    name: str
    type: StorageType

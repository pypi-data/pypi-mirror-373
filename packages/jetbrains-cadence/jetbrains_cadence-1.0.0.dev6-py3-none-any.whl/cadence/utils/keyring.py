from keyring import get_password as keyring_get_password
from pydantic import ValidationError

from cadence.api.model.storage import Storage

SERVICE_NAME_PREFIX: str = "IntelliJ Platform"
SUBSYSTEM: str = "Cadence"
PREFIX: str = "STORAGE_"


def generate_intellij_service_name(name: str) -> str:
    key = PREFIX + name
    service_name = f"{SERVICE_NAME_PREFIX} {SUBSYSTEM} — {key}"
    return service_name


def get_storage(name: str) -> Storage | None:
    storage_str = keyring_get_password(generate_intellij_service_name(name), "")
    if storage_str is None:
        return None

    try:
        return Storage.model_validate_json(storage_str, by_alias=True)
    except ValidationError:
        return None

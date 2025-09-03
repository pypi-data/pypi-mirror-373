import json
from pathlib import Path
from typing import Any

CADENCE_CONFIG_DIR_PATH = Path.home() / '.config' / 'cadence'


def read_cadence_config(path: Path | None = None) -> dict[str, Any] | None:
    if path is None:
        CADENCE_CONFIG_DIR_PATH.mkdir(parents=True, exist_ok=True)
        path = CADENCE_CONFIG_DIR_PATH / 'config.json'
        if not path.exists():
            return None

    with path.open('r') as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            return None


def write_cadence_config(config: dict[str, Any], path: Path | None = None) -> None:
    if path is None:
        CADENCE_CONFIG_DIR_PATH.mkdir(parents=True, exist_ok=True)
        path = CADENCE_CONFIG_DIR_PATH / 'config.json'

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as file:
        json.dump(config, file, indent=2)

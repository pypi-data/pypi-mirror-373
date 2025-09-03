import os
import subprocess
import warnings
from typing import Optional

import click
from click import Context, Parameter
from click.shell_completion import CompletionItem

from cadence.api.model.Execution import Execution
from cadence.api.model.JetTrainConfig import JetTrainConfig
from cadence.api.model.StorageType import StorageType


def needs_default_storage(config: JetTrainConfig) -> bool:
    return ((config.project_sync.local and config.project_sync.local.storage_type == StorageType.DEFAULT) or
            any(i.storage_type == StorageType.DEFAULT for i in config.inputs) or
            any(o.storage_type == StorageType.DEFAULT for o in config.outputs))


def run_cmd(cmd: str, *, env: Optional[dict[str, str]] = None, retries_count: int = 10,
            check_return_code: bool = True) -> None:
    if not env:
        env = os.environ.copy()

    p = None
    for i in range(retries_count + 1):
        if i > 0:
            warnings.warn(f"Retrying cmd...\n{cmd}")

        p = subprocess.Popen(cmd, shell=True, env=env)
        p.wait()

        if not check_return_code or p.returncode == 0:
            break
    if check_return_code and p and p.returncode != 0:
        raise ValueError(f"Execution of command\n{cmd}\nfailed with rc {p.returncode}")


EXECUTION_DEFAULT_EXCLUDE_KEYS = {'mounts', 'metadata', 'credentialsById'}


class ExecutionKey(click.ParamType):
    name = "execution"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> list[CompletionItem]:
        return [CompletionItem(key) for key in Execution.model_fields.keys() if
                key not in EXECUTION_DEFAULT_EXCLUDE_KEYS and key.startswith(incomplete)]

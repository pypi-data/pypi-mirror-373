import os

from cadence.api.model.JetTrainConfig import JetTrainConfig
from cadence.api.model.common import Input, S3Credentials
from cadence.api.model.connector import S3Connector
from cadence.api.model.storage import Storage, DefaultStorage
from cadence.api.utils import run_cmd

DEFAULT_EXCLUDE_SYNC_LIST = ["**/.mypy_cache/*", ".mypy_cache/*", "**/__pycache__/*", "__pycache__/*",
                             "**/.pytest_cache/*", ".pytest_cache/*", "**/.venv/*", ".venv/*", "**/venv/*", "venv/*",
                             ".jettrain/*", "**/.jettrain/*", ".git/*", "**/.git/*", ".cadence/*"]


def process_project_local_sync(project_sync: JetTrainConfig.ProjectSyncConf.LocalProjectSyncConf,
                               storage: Storage) -> Input:
    from_path = project_sync.root

    if isinstance(storage, DefaultStorage):
        to_path = f"{storage.base_uri}/data/"
    else:
        to_path = f"s3://{storage.bucket}/{project_sync.uri}/"

    return Input(path=from_path, connector=S3Connector(uri=to_path, credentialsId=project_sync.storage_name,
                                                       storageType=project_sync.storage_type, ))


def s3_sync_local_to_remote(from_path: str, to_path: str, storage: Storage, *, include: list[str],
                            exclude: list[str]) -> None:
    endpoint_url = f"--endpoint-url {storage.endpoint_url}" if storage.endpoint_url else ""
    exclude_str = ' '.join([f"--exclude '{e}'" for e in exclude + DEFAULT_EXCLUDE_SYNC_LIST])
    include_str = ' '.join([f"--include '{e}'" for e in include])
    cmd = f"aws s3 sync {from_path} {to_path} {exclude_str} {include_str} {endpoint_url} --delete --checksum-algorithm=SHA256"

    env = os.environ.copy()
    if storage.access_key_id:
        env["AWS_ACCESS_KEY_ID"] = storage.access_key_id
    if storage.secret_access_key:
        env["AWS_SECRET_ACCESS_KEY"] = storage.secret_access_key
    if storage.session_token:
        env["AWS_SESSION_TOKEN"] = storage.session_token

    run_cmd(cmd, env=env, check_return_code=False)


def s3_sync_remote_to_local(from_path: str, to_path: str, credentials: S3Credentials) -> None:
    recursive = "--recursive" if from_path.endswith("/") else ""
    cmd = f"aws s3 cp {from_path} {to_path} {recursive}"

    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = credentials.accessKeyId
    env["AWS_SECRET_ACCESS_KEY"] = credentials.secretAccessKey
    if credentials.sessionToken:
        env["AWS_SESSION_TOKEN"] = credentials.sessionToken

    run_cmd(cmd, env=env, check_return_code=False)

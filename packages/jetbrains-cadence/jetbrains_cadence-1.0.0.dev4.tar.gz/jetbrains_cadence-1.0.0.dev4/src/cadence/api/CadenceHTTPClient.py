from importlib.metadata import version
from typing import Generator, Any

import httpx
from pydantic import BaseModel

from cadence.api.exceptions import CadenceServerException
from cadence.api.model.Execution import Execution, ExecutionList
from cadence.api.model.Project import Project, ProjectList
from cadence.api.model.ProjectView import ProjectView, ProjectViewList
from cadence.api.model.Provisioning import ProvisioningList, Provisioning
from cadence.api.model.StartExecutionRequest import StartExecutionRequest
from cadence.api.model.StorageType import StorageType
from cadence.api.model.User import User
from cadence.api.model.common import S3Credentials
from cadence.api.model.logs import ExecutionLogs
from cadence.api.model.storage import DefaultStorage

DEFAULT_SERVER_URL: str = "https://api.cadence.jetbrains.com"
API_ENDPOINT: str = "/app/jettrain/api/v0"
TIMEOUT: int = 30

CADENCE_CLI_VERSION = version("jetbrains-cadence")


class CadenceHTTPClient:
    def __init__(self, server_url: str, token: str):
        headers = {"Content-Type": "application/json", "User-Agent": f"cadenceCLI/{CADENCE_CLI_VERSION}",
                   "Authorization": f"Bearer {token}", }
        self.client = httpx.Client(headers=headers, base_url=server_url + API_ENDPOINT)

    def validate_execution_request(self, project_id: str, request: StartExecutionRequest) -> None:
        response = self.client.post(f"/projects/{project_id}/executions/_validate", json=request.to_dict())
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

    def start_execution(self, project_id: str, request: StartExecutionRequest) -> Execution:
        response = self.client.post(f"/projects/{project_id}/executions", json=request.to_dict())
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return Execution.model_validate(response.json())

    def get_execution(self, project_id: str, execution_id: str) -> Execution:
        response = self.client.get(f"/projects/{project_id}/executions/{execution_id}")
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return Execution.model_validate(response.json())

    def get_execution_status(self, project_id: str, execution_id: str) -> str:  # TODO make enum
        response = self.client.get(f"/projects/{project_id}/executions/{execution_id}/status")
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return str(response.json())

    def cancel_execution(self, project_id: str, execution_id: str) -> Execution:
        response = self.client.post(f"/projects/{project_id}/executions/{execution_id}/_cancel")
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return Execution.model_validate(response.json())

    def get_executions_list(self, project_id: str, offset: int, count: int) -> ExecutionList:
        response = self.client.get(f"/projects/{project_id}/executions", params={"offset": offset, "count": count})
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return ExecutionList.model_validate(response.json())

    def generate_temporary_credentials(self, project_id: str) -> 'TemporaryS3Data':
        response = self.client.post("/storage/_generateCredentials", params={"projectId": project_id})
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return TemporaryS3Data.model_validate(response.json())

    def get_current_user(self) -> User:
        response = self.client.get("/users/current")
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return User.model_validate(response.json())

    def get_project_views(self) -> list[ProjectView]:
        response = self.client.get("/projects/views")
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return ProjectViewList.model_validate(response.json()).projectViews

    def get_project(self, project_id: str) -> Project | None:
        response = self.client.get(f"/projects/{project_id}")
        if not response.is_success:
            if response.status_code == 400 or response.status_code == 404:
                return None
            raise CadenceServerException(response.text, status=response.status_code)

        return Project.model_validate(response.json())

    def get_projects(self) -> ProjectList:
        response = self.client.get("/projects")

        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return ProjectList.model_validate(response.json())

    def get_available_provisioning(
            self,
            project_id: str,
            include_unavailable: bool
    ) -> list[Provisioning]:
        response = self.client.get(f"/projects/{project_id}/provisioning")
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return ProvisioningList.model_validate(response.json()).provisioningList

    def get_current_execution_log_offset(self, project_id: str, execution_id: str) -> int:
        response = self.client.get(f"/projects/{project_id}/executions/{execution_id}/logs/current_offset")

        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return int(response.json())


    def get_execution_logs(self, project_id: str, execution_id: str, offset: int, count: int) -> ExecutionLogs:
        response = self.client.get(f"/projects/{project_id}/executions/{execution_id}/logs/stream", params={"offset": offset, "count": count})
        if not response.is_success:
            raise CadenceServerException(response.text, status=response.status_code)

        return ExecutionLogs.model_validate(response.json())


class TemporaryAwsCredentials(BaseModel):
    accessKeyId: str
    secretAccessKey: str
    sessionToken: str
    expiresAt: str


class TemporaryS3Data(BaseModel):
    bucket: str
    allowedPrefix: str
    credentials: TemporaryAwsCredentials

    def to_s3_credentials(self):
        return S3Credentials(accessKeyId=self.credentials.accessKeyId,
                             secretAccessKey=self.credentials.secretAccessKey,
                             sessionToken=self.credentials.sessionToken)

    def to_default_storage(self, username: str):
        return DefaultStorage(accessKeyId=self.credentials.accessKeyId,
                              secretAccessKey=self.credentials.secretAccessKey,
                              sessionToken=self.credentials.sessionToken,
                              bucket=self.bucket,
                              type=StorageType.DEFAULT,
                              prefix=self.allowedPrefix,
                              username=username)


def all_executions(client: CadenceHTTPClient, project_id: str, *, batch_size: int = 50) -> Generator[
    Execution, Any, Any]:
    count: int = 0
    executions: ExecutionList | None = None
    while True:
        if count % batch_size == 0:
            executions = client.get_executions_list(project_id=project_id, offset=count, count=batch_size)
        if executions.count == 0 or count >= executions.totalCount:
            return
        count += executions.count
        yield from executions.executions

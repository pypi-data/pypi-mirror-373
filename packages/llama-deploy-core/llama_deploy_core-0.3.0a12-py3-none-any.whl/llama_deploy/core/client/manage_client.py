import contextlib
from typing import Iterator, List

import httpx
from llama_deploy.core.schema.base import LogEvent
from llama_deploy.core.schema.deployments import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentsListResponse,
    DeploymentUpdate,
)
from llama_deploy.core.schema.git_validation import (
    RepositoryValidationRequest,
    RepositoryValidationResponse,
)
from llama_deploy.core.schema.projects import ProjectsListResponse, ProjectSummary


class ClientError(Exception):
    """Base class for client errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BaseClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            event_hooks={"response": [self._handle_response]},
        )
        self.hookless_client = httpx.Client(base_url=self.base_url)

    def _handle_response(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                response.read()
                error_data = e.response.json()
                if isinstance(error_data, dict) and "detail" in error_data:
                    error_message = error_data["detail"]
                else:
                    error_message = str(error_data)
            except (ValueError, KeyError):
                error_message = e.response.text
            raise ClientError(f"HTTP {e.response.status_code}: {error_message}") from e
        except httpx.RequestError as e:
            raise ClientError(f"Request failed: {e}") from e


class ControlPlaneClient(BaseClient):
    """Unscoped client for non-project endpoints."""

    def health_check(self) -> dict:
        response = self.client.get("/health")
        return response.json()

    def server_version(self) -> dict:
        response = self.client.get("/version")
        return response.json()

    def list_projects(self) -> List[ProjectSummary]:
        response = self.client.get("/api/v1beta1/deployments/list-projects")
        projects_response = ProjectsListResponse.model_validate(response.json())
        return [project for project in projects_response.projects]


class ProjectClient(BaseClient):
    """Project-scoped client for deployment operations."""

    def __init__(
        self,
        base_url: str,
        project_id: str,
    ) -> None:
        super().__init__(base_url)
        self.project_id = project_id

    def list_deployments(self) -> List[DeploymentResponse]:
        response = self.client.get(
            "/api/v1beta1/deployments",
            params={"project_id": self.project_id},
        )
        deployments_response = DeploymentsListResponse.model_validate(response.json())
        return [deployment for deployment in deployments_response.deployments]

    def get_deployment(
        self, deployment_id: str, include_events: bool = False
    ) -> DeploymentResponse:
        response = self.client.get(
            f"/api/v1beta1/deployments/{deployment_id}",
            params={"project_id": self.project_id, "include_events": include_events},
        )
        return DeploymentResponse.model_validate(response.json())

    def create_deployment(
        self, deployment_data: DeploymentCreate
    ) -> DeploymentResponse:
        response = self.client.post(
            "/api/v1beta1/deployments",
            params={"project_id": self.project_id},
            json=deployment_data.model_dump(exclude_none=True),
        )
        return DeploymentResponse.model_validate(response.json())

    def delete_deployment(self, deployment_id: str) -> None:
        self.client.delete(
            f"/api/v1beta1/deployments/{deployment_id}",
            params={"project_id": self.project_id},
        )

    def update_deployment(
        self,
        deployment_id: str,
        update_data: DeploymentUpdate,
    ) -> DeploymentResponse:
        response = self.client.patch(
            f"/api/v1beta1/deployments/{deployment_id}",
            params={"project_id": self.project_id},
            json=update_data.model_dump(),
        )
        return DeploymentResponse.model_validate(response.json())

    def validate_repository(
        self,
        repo_url: str,
        deployment_id: str | None = None,
        pat: str | None = None,
    ) -> RepositoryValidationResponse:
        response = self.client.post(
            "/api/v1beta1/deployments/validate-repository",
            params={"project_id": self.project_id},
            json=RepositoryValidationRequest(
                repository_url=repo_url,
                deployment_id=deployment_id,
                pat=pat,
            ).model_dump(),
        )
        return RepositoryValidationResponse.model_validate(response.json())

    def stream_deployment_logs(
        self,
        deployment_id: str,
        *,
        include_init_containers: bool = False,
        since_seconds: int | None = None,
        tail_lines: int | None = None,
    ) -> tuple["Closer", Iterator[LogEvent]]:
        """Stream logs as LogEvent items from the control plane using SSE.

        This yields `LogEvent` models until the stream ends (e.g. rollout).
        """
        # Use a separate client without response hooks so we don't consume the stream

        params = {
            "project_id": self.project_id,
            "include_init_containers": include_init_containers,
        }
        if since_seconds is not None:
            params["since_seconds"] = since_seconds
        if tail_lines is not None:
            params["tail_lines"] = tail_lines

        url = f"/api/v1beta1/deployments/{deployment_id}/logs"
        headers = {"Accept": "text/event-stream"}

        stack = contextlib.ExitStack()
        response = stack.enter_context(
            self.hookless_client.stream(
                "GET", url, params=params, headers=headers, timeout=None
            )
        )
        try:
            response.raise_for_status()
        except Exception:
            stack.close()
            raise

        return stack.close, _iterate_log_stream(response, stack.close)


def _iterate_log_stream(
    response: httpx.Response, closer: "Closer"
) -> Iterator[LogEvent]:
    event_name: str | None = None
    data_lines: list[str] = []

    try:
        for line in response.iter_lines():
            if line is None:
                continue
            line = line.decode() if isinstance(line, (bytes, bytearray)) else line
            print("got line", line)
            if line.startswith("event:"):
                event_name = line[len("event:") :].strip()
            elif line.startswith("data:"):
                data_lines.append(line[len("data:") :].lstrip())
            elif line.strip() == "":
                if event_name == "log" and data_lines:
                    data_str = "\n".join(data_lines)
                    try:
                        yield LogEvent.model_validate_json(data_str)
                        print("yielded log event", data_str)
                    except Exception:
                        # If parsing fails, skip malformed event
                        pass
                # reset for next event
                event_name = None
                data_lines = []
    finally:
        try:
            closer()
        except Exception:
            pass


type Closer = callable[tuple[()], None]

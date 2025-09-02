from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import HttpUrl

from .base import Base

# K8s CRD phase values
LlamaDeploymentPhase = Literal[
    "Syncing",  # Initial reconciliation phase - controller is processing the deployment
    "Pending",  # Waiting for deployment resources to be ready (pods starting up)
    "Running",  # Deployment is healthy and serving traffic
    "Failed",  # Complete deployment failure - no pods available
    "Succeeded",  # Deployment completed successfully (for one-time jobs)
    "RollingOut",  # Rolling update in progress - new pods being created while old ones still serve traffic
    "RolloutFailed",  # New deployment failed but old pods are still available and serving traffic
]


class DeploymentEvent(Base):
    message: str | None = None
    reason: str | None = None
    type: str | None = None
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    count: int | None = None


class DeploymentResponse(Base):
    id: str
    name: str
    repo_url: str
    deployment_file_path: str
    git_ref: str | None = None
    git_sha: str | None = None
    has_personal_access_token: bool = False
    project_id: str
    secret_names: list[str] | None = None
    apiserver_url: HttpUrl | None
    status: LlamaDeploymentPhase
    warning: str | None = None
    events: list[DeploymentEvent] | None = None


class DeploymentsListResponse(Base):
    deployments: list[DeploymentResponse]


class DeploymentCreate(Base):
    name: str
    repo_url: str
    deployment_file_path: str | None = None
    git_ref: str | None = None
    personal_access_token: str | None = None
    secrets: dict[str, str] | None = None


class LlamaDeploymentMetadata(Base):
    name: str
    namespace: str
    uid: str | None = None
    resourceVersion: str | None = None
    creationTimestamp: datetime | None = None
    annotations: dict[str, str] | None = None
    labels: dict[str, str] | None = None


class LlamaDeploymentSpec(Base):
    """
    LlamaDeployment spec fields as defined in the Kubernetes CRD.

    Maps to the spec section of the LlamaDeployment custom resource.
    Field names match exactly with the K8s CRD for direct conversion.
    """

    projectId: str
    repoUrl: str
    deploymentFilePath: str = "."
    gitRef: str | None = None
    gitSha: str | None = None
    name: str
    secretName: str | None = None
    # when true, the deployment will prebuild the UI assets and serve them from a static file server
    staticAssetsPath: str | None = None


class LlamaDeploymentStatus(Base):
    """
    LlamaDeployment status fields as defined in the Kubernetes CRD.

    Maps to the status section of the LlamaDeployment custom resource.
    """

    phase: LlamaDeploymentPhase | None = None
    message: str | None = None
    lastUpdated: datetime | None = None
    authToken: str | None = None


class LlamaDeploymentCRD(Base):
    metadata: LlamaDeploymentMetadata
    spec: LlamaDeploymentSpec
    status: LlamaDeploymentStatus


class DeploymentUpdate(Base):
    """
    Patch-style update model for deployments.

    Fields not included in the request will remain unchanged.
    Fields explicitly set to None will clear/delete the field value.

    For secrets: provide a dict where string values add/update secrets
    and null values remove secrets.
    """

    repo_url: str | None = None
    deployment_file_path: str | None = None
    git_ref: str | None = None
    git_sha: str | None = None
    personal_access_token: str | None = None
    secrets: dict[str, str | None] | None = None
    static_assets_path: Path | None = None


class DeploymentUpdateResult(Base):
    """
    Result of applying a DeploymentUpdate to a LlamaDeploymentSpec.

    Contains the updated spec and lists of secret changes to apply.
    """

    updated_spec: LlamaDeploymentSpec
    secret_adds: dict[str, str]
    secret_removes: list[str]


def apply_deployment_update(
    update: DeploymentUpdate,
    existing_spec: LlamaDeploymentSpec,
) -> DeploymentUpdateResult:
    """
    Apply a DeploymentUpdate to an existing LlamaDeploymentSpec.

    Returns the updated spec and lists of secret changes.

    Args:
        update: The update to apply (snake_case fields from API)
        existing_spec: The current LlamaDeploymentSpec (camelCase fields)
        git_sha: The resolved git SHA to set

    Returns:
        DeploymentUpdateResult with updated spec and secret changes
    """
    # Start with a copy of the existing spec
    updated_spec = existing_spec.model_copy()

    # Apply direct field updates (only if not None)
    # Convert from snake_case API fields to camelCase spec fields
    if update.repo_url is not None:
        updated_spec.repoUrl = update.repo_url

    if update.deployment_file_path is not None:
        updated_spec.deploymentFilePath = update.deployment_file_path

    if update.git_ref is not None:
        updated_spec.gitRef = update.git_ref

    # Update gitSha if provided
    if update.git_sha is not None:
        updated_spec.gitSha = None if update.git_sha == "" else update.git_sha

    # always apply this, as it should be cleared out if none, and is only set by the server
    updated_spec.staticAssetsPath = (
        str(update.static_assets_path) if update.static_assets_path else None
    )

    # Track secret changes
    secret_adds: dict[str, str] = {}
    secret_removes: list[str] = []

    # Handle personal access token (stored as GITHUB_PAT secret)
    if update.personal_access_token is not None:
        if update.personal_access_token == "":
            # Empty string means remove the PAT
            secret_removes.append("GITHUB_PAT")
        else:
            # Non-empty string means add/update the PAT
            secret_adds["GITHUB_PAT"] = update.personal_access_token

    # Handle explicit secret updates
    secrets = update.secrets
    if secrets is not None:
        for key, value in secrets.items():
            if value is None:
                # None means remove this secret
                secret_removes.append(key)
            else:
                # String value means add/update this secret
                secret_adds[key] = value

    return DeploymentUpdateResult(
        updated_spec=updated_spec,
        secret_adds=secret_adds,
        secret_removes=secret_removes,
    )


class LogEvent(Base):
    pod: str
    container: str
    text: str
    timestamp: datetime

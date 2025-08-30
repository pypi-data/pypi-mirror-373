from .base import Base


class ProjectSummary(Base):
    """Summary of a project with deployment count"""

    project_id: str
    deployment_count: int


class ProjectsListResponse(Base):
    """Response model for listing projects with deployment counts"""

    projects: list[ProjectSummary]

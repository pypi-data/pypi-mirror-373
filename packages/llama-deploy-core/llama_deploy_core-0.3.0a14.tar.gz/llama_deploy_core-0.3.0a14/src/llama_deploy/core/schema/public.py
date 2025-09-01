from .base import Base


class VersionResponse(Base):
    version: str
    requires_auth: bool = False
    min_llamactl_version: str | None = None

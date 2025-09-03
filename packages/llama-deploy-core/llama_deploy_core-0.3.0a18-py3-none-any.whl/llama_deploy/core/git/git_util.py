"""
Git utilities for the purpose of exploring, cloning, and parsing llama-deploy repositories.
Responsibilities are lower level git access, as well as some application specific config parsing.
"""

import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml


def parse_github_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL to extract owner and repo name.

    Args:
        repo_url: GitHub repository URL (various formats supported)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValueError: If URL format is not recognized
    """
    # Remove .git suffix if present
    url = repo_url.rstrip("/").removesuffix(".git")

    # Handle different GitHub URL formats
    patterns = [
        r"https://github\.com/([^/]+)/([^/]+)",
        r"git@github\.com:([^/]+)/([^/]+)",
        r"github\.com/([^/]+)/([^/]+)",
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1), match.group(2)

    raise ValueError(f"Could not parse GitHub repository URL: {repo_url}")


def inject_basic_auth(url: str, basic_auth: str | None = None) -> str:
    """Inject basic auth into a URL if provided"""
    if basic_auth and "://" in url and "@" not in url:
        scheme, rest = url.split("://", 1)
        url = f"{scheme}://{basic_auth}@{rest}"
    return url


def _run_process(args: list[str], cwd: str | None = None, timeout: int = 30) -> str:
    """Run a process and raise a GitAccessError with detailed output if it fails.

    The error message includes the command, return code, working directory,
    and both stdout and stderr to aid debugging (e.g., git fetch failures).
    """
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        cmd = " ".join(args)
        where = f" (cwd={cwd})" if cwd else ""
        raise GitAccessError(f"Command timed out after {timeout}s: {cmd}{where}")

    if result.returncode != 0:
        cmd = " ".join(args)
        where = f" (cwd={cwd})" if cwd else ""
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        details = []
        if stdout:
            details.append(f"stdout:\n{stdout}")
        if stderr:
            details.append(f"stderr:\n{stderr}")
        detail_block = "\n\n".join(details) if details else "(no output)"
        raise GitAccessError(
            f"Command failed with exit code {result.returncode}: {cmd}{where}\n{detail_block}"
        )

    return (result.stdout or "").strip()


class GitAccessError(Exception):
    """Error raised when a user reportable git error occurs, e.g connection fails, cannot access repository, timeout, ref not found, etc."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@dataclass
class GitCloneResult:
    git_sha: str
    git_ref: str | None = None


def clone_repo(
    repository_url: str,
    git_ref: str | None = None,
    basic_auth: str | None = None,
    dest_dir: Path | str | None = None,
) -> GitCloneResult:
    """
    Clone a repository and checkout a specific ref, if provided. If user reportable access errors occur, raises a GitAccessError.

    Args:
        repository_url: The URL of the repository to clone
        git_ref: The git reference to checkout, if provided
        basic_auth: The basic auth to use to clone the repository
        dest_dir: The directory to clone the repository to, if provided

    Returns:
        GitCloneResult: A dataclass containing the git SHA and resolved git ref (e.g. main if None was provided)
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir) if dest_dir is None else Path(dest_dir)
            authenticated_url = inject_basic_auth(repository_url, basic_auth)
            did_exist = (
                dest_dir.exists() and dest_dir.is_dir() and list(dest_dir.iterdir())
            )
            if not did_exist:
                # need to do a full clone to resolve any kind of ref without exploding in
                # complexity (tag, branch, commit, short commit)
                clone_args = [
                    "git",
                    "clone",
                    authenticated_url,
                    str(dest_dir.absolute()),
                ]
                _run_process(clone_args)

            if not git_ref:
                resolved_branch = _run_process(
                    ["git", "branch", "--show-current"],
                    cwd=str(dest_dir.absolute()),
                )
                if resolved_branch:
                    git_ref = resolved_branch
                else:
                    # Try exact tag match; if it fails, we just ignore and proceed
                    try:
                        resolved_tag = _run_process(
                            ["git", "describe", "--tags", "--exact-match"],
                            cwd=str(dest_dir.absolute()),
                        )
                        if resolved_tag:
                            git_ref = resolved_tag
                    except GitAccessError:
                        pass
            else:  # Checkout the ref
                if did_exist:
                    _run_process(
                        ["git", "fetch", "origin"], cwd=str(dest_dir.absolute())
                    )
                _run_process(["git", "checkout", git_ref], cwd=str(dest_dir.absolute()))
            # if no ref, stay on whatever the clone gave us/current commit
            # return the resolved sha
            resolved_sha = _run_process(
                ["git", "rev-parse", "HEAD"], cwd=str(dest_dir.absolute())
            ).strip()
            return GitCloneResult(git_sha=resolved_sha, git_ref=git_ref)
    except GitAccessError:
        # Re-raise enriched errors from _run_process directly
        raise
    except subprocess.TimeoutExpired:
        raise GitAccessError("Timeout while cloning repository")


def validate_deployment_file(repo_dir: Path, deployment_file_path: str) -> bool:
    """
    Validate that the deployment file exists in the repository.

    Args:
        repo_dir: The directory of the repository
        deployment_file_path: The path to the deployment file, relative to the repository root

    Returns:
        True if the deployment file exists and appears to be valid, False otherwise
    """
    deployment_file = repo_dir / deployment_file_path
    if not deployment_file.exists():
        return False
    with open(deployment_file, "r") as f:
        try:
            loaded = yaml.safe_load(f)
            if not isinstance(loaded, dict):
                return False
            if "name" not in loaded:
                return False
            if not isinstance(loaded["name"], str):
                return False
            if "services" not in loaded:
                return False
            if not isinstance(loaded["services"], dict):
                return False
            return True  # good nuff for now. Eventually this should parse it into a model validated format
        except yaml.YAMLError:
            return False


def validate_git_public_access(repository_url: str) -> bool:
    """Check if a git repository is publicly accessible using git ls-remote."""

    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repository_url],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,  # Don't raise on non-zero exit
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def validate_git_credential_access(repository_url: str, basic_auth: str) -> bool:
    """Check if a credential provides access to a git repository."""

    auth_url = inject_basic_auth(repository_url, basic_auth)
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", auth_url],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def is_git_repo() -> bool:
    """
    checks if the cwd is a git repo
    """
    try:
        _run_process(["git", "status"])
        return True
    except GitAccessError:
        return False


def list_remotes() -> list[str]:
    """
    list the remote urls for the current git repo
    """
    result = _run_process(["git", "remote", "-v"])
    return [line.split()[1] for line in result.splitlines()]


def get_current_branch() -> str | None:
    """
    get the current branch for the current git repo
    """
    result = _run_process(["git", "branch", "--show-current"])
    return result.strip() if result.strip() else None


def get_git_root() -> Path:
    """
    get the root of the current git repo
    """
    result = _run_process(["git", "rev-parse", "--show-toplevel"])
    return Path(result.strip())

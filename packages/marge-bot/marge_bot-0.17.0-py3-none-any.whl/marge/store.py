import abc
import dataclasses
import datetime
import tempfile
from typing import TYPE_CHECKING, Optional

from . import git
from . import project as mb_project
from . import user as mb_user


@dataclasses.dataclass
class RepoManager(abc.ABC):
    user: mb_user.User
    root_dir: str
    timeout: Optional[datetime.timedelta] = None
    reference: Optional[str] = None
    keep_committers: bool = False

    def __post_init__(self) -> None:
        self._repos: dict[int, git.Repo] = {}

    @abc.abstractmethod
    def _get_project_url(self, project: mb_project.Project) -> str: ...

    @abc.abstractmethod
    def _git_repo(self, repo_url: str, local_repo_dir: str) -> git.Repo: ...

    def repo_for_project(self, project: mb_project.Project) -> git.Repo:
        repo = self._repos.get(project.id)
        if not repo or repo.remote_url != self._get_project_url(project):
            repo_url = self._get_project_url(project)
            local_repo_dir = tempfile.mkdtemp(dir=self.root_dir)

            repo = self._git_repo(repo_url, local_repo_dir)
            repo.clone()
            repo.configure()

            self._repos[project.id] = repo

        return repo


@dataclasses.dataclass
class SshRepoManager(RepoManager):
    ssh_key_file: Optional[str] = None

    def _get_project_url(self, project: mb_project.Project) -> str:
        return project.ssh_url_to_repo

    def _git_repo(self, repo_url: str, local_repo_dir: str) -> git.Repo:
        if TYPE_CHECKING:
            assert self.user.email is not None
        return git.Repo(
            repo_url,
            local_repo_dir,
            self.user.email,
            self.user.name,
            ssh_key_file=self.ssh_key_file,
            timeout=self.timeout,
            reference=self.reference,
            keep_committers=self.keep_committers,
        )


@dataclasses.dataclass
class HttpsRepoManager(RepoManager):
    auth_token: Optional[str] = None

    def _get_project_url(self, project: mb_project.Project) -> str:
        return project.http_url_to_repo

    def _git_repo(self, repo_url: str, local_repo_dir: str) -> git.Repo:
        if TYPE_CHECKING:
            assert self.auth_token is not None
            assert self.user.email is not None
        return git.Repo(
            repo_url,
            local_repo_dir,
            self.user.email,
            self.user.name,
            ssh_key_file=None,
            timeout=self.timeout,
            reference=self.reference,
            auth_token=self.auth_token,
            keep_committers=self.keep_committers,
        )

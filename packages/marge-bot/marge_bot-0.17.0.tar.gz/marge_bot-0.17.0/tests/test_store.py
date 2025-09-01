import os.path
from unittest import mock

import pytest

import marge.git
import marge.store
import marge.user
from tests.test_git import get_calls as get_git_calls
from tests.test_project import INFO as PRJ_INFO
from tests.test_user import INFO as USER_INFO


# pylint: disable=attribute-defined-outside-init
@mock.patch("marge.git._run")
class TestRepoManager:
    @pytest.fixture
    def user(self):
        return marge.user.User(
            api=None,
            info=dict(USER_INFO, name="Peter Parker", email="pparker@bugle.com"),
        )

    @pytest.fixture
    def ssh_repo_manager(self, user, tmp_path):
        return marge.store.SshRepoManager(
            user=user, root_dir=str(tmp_path), ssh_key_file="/ssh/key"
        )

    @pytest.fixture
    def https_repo_manager(self, user, tmp_path):
        return marge.store.HttpsRepoManager(
            user=user, root_dir=str(tmp_path), auth_token="glpat-TEST"
        )

    def new_project(self, project_id, path_with_namespace):
        schemeless_url_to_repo = f"buh.com/{path_with_namespace}.git"
        info = dict(
            PRJ_INFO,
            id=project_id,
            path_with_namespace=path_with_namespace,
            ssh_url_to_repo=f"ssh://{schemeless_url_to_repo}",
            http_url_to_repo=f"https://{schemeless_url_to_repo}",
        )
        return marge.project.Project(api=None, info=info)

    def test_creates_and_initializes_repo(self, git_run, ssh_repo_manager):
        project = self.new_project(1234, "some/stuff")

        git_run.assert_not_called()

        repo = ssh_repo_manager.repo_for_project(project)

        assert os.path.dirname(repo.local_path) == ssh_repo_manager.root_dir
        assert repo.local_path != ssh_repo_manager.root_dir

        env = (
            f"GIT_SSH_COMMAND='{marge.git.GIT_SSH_COMMAND} -F /dev/null "
            f"-o IdentitiesOnly=yes -i /ssh/key'"
        )
        assert get_git_calls(git_run) == [
            f"{env} git clone --origin=origin --filter=blob:none {project.ssh_url_to_repo} "
            f"{repo.local_path}",
            f"{env} git -C {repo.local_path} config user.email pparker@bugle.com",
            f"{env} git -C {repo.local_path} config user.name 'Peter Parker'",
            f"{env} git -C {repo.local_path} config gpg.format ssh",
            f"{env} git -C {repo.local_path} config user.signingKey /ssh/key",
        ]

    def test_caches_repos_by_id(self, git_run, ssh_repo_manager):
        project = self.new_project(1234, "some/stuff")
        same_project = marge.project.Project(
            api=None, info=dict(project.info, name="same/stuff")
        )

        assert git_run.call_count == 0

        repo_first_call = ssh_repo_manager.repo_for_project(project)
        assert git_run.call_count == 5

        repo_second_call = ssh_repo_manager.repo_for_project(same_project)
        assert repo_second_call is repo_first_call
        assert git_run.call_count == 5

    def test_stops_caching_if_ssh_url_changed(self, git_run, ssh_repo_manager):
        project = self.new_project(1234, "some/stuff")

        assert git_run.call_count == 0

        repo_first_call = ssh_repo_manager.repo_for_project(project)
        assert git_run.call_count == 5

        different_ssh_url = self.new_project(1234, "same/stuff")

        repo_second_call = ssh_repo_manager.repo_for_project(different_ssh_url)
        assert git_run.call_count == 10
        assert (
            repo_first_call.remote_url
            != repo_second_call.remote_url
            == different_ssh_url.ssh_url_to_repo
        )

    def test_handles_different_projects(self, git_run, ssh_repo_manager):
        project_1 = self.new_project(1234, "some/stuff")
        project_2 = self.new_project(5678, "other/things")

        assert git_run.call_count == 0

        repo_1 = ssh_repo_manager.repo_for_project(project_1)
        assert git_run.call_count == 5

        repo_2 = ssh_repo_manager.repo_for_project(project_2)
        assert git_run.call_count == 10

        assert repo_1.local_path != repo_2.local_path

    def test_no_dups_with_token(self, git_run, https_repo_manager):
        project = self.new_project(1234, "some/stuff")

        assert git_run.call_count == 0

        repo_initial = https_repo_manager.repo_for_project(project)
        assert git_run.call_count == 3

        repo_repeat = https_repo_manager.repo_for_project(project)
        # Call count should not have changed as the repo is cached.
        assert git_run.call_count == 3

        assert repo_initial.local_path == repo_repeat.local_path

import collections
import dataclasses
import datetime
import logging as log
import re
import time
from tempfile import TemporaryDirectory
from typing import Optional

from . import batch_job, git, gitlab, job
from . import merge_request as merge_request_module
from . import single_merge_job, store
from . import user as user_module
from .project import Project

MergeRequest = merge_request_module.MergeRequest


class Bot:
    def __init__(self, *, api: gitlab.Api, config: "BotConfig"):
        self._api = api
        self._config = config

        user = config.user
        opts = config.merge_opts

        if not user.is_admin:
            assert (
                not opts.reapprove
            ), f"{user.username} is not an admin, can't impersonate!"
            assert (
                not opts.add_reviewers
            ), f"{user.username} is not an admin, can't lookup Reviewed-by: email addresses "

    def start(self) -> None:
        with TemporaryDirectory() as root_dir:
            repo_manager: store.RepoManager
            if self._config.use_https:
                repo_manager = store.HttpsRepoManager(
                    user=self.user,
                    root_dir=root_dir,
                    auth_token=self._config.auth_token,
                    timeout=self._config.git_timeout,
                    reference=self._config.git_reference_repo,
                    keep_committers=self._config.merge_opts.keep_committers,
                )
            else:
                repo_manager = store.SshRepoManager(
                    user=self.user,
                    root_dir=root_dir,
                    ssh_key_file=self._config.ssh_key_file,
                    timeout=self._config.git_timeout,
                    reference=self._config.git_reference_repo,
                    keep_committers=self._config.merge_opts.keep_committers,
                )
            self._run(repo_manager)

    @property
    def user(self) -> user_module.User:
        return self._config.user

    @property
    def api(self) -> gitlab.Api:
        return self._api

    def _run(self, repo_manager: store.RepoManager) -> None:
        sleep_time_between_iterations = 30
        while True:
            pending_merge_requests = self._get_assigned_merge_requests()
            for project, merge_requests in pending_merge_requests.items():
                self._process_merge_requests(repo_manager, project, merge_requests)
            if self._config.cli:
                return

            log.info("Sleeping for %s seconds...", sleep_time_between_iterations)
            time.sleep(sleep_time_between_iterations)

    def _get_assigned_merge_requests(self) -> dict[Project, list[MergeRequest]]:
        log.info("Fetching merge requests assigned to me...")
        project_merge_requests = collections.defaultdict(list)
        branch_regexp = self._config.branch_regexp
        source_branch_regexp = self._config.source_branch_regexp
        assigned_merge_requests = MergeRequest.fetch_all_mine(
            self._api, self.user, self._config.merge_order
        )
        for merge_request in assigned_merge_requests:
            project_id = merge_request.project_id
            if not branch_regexp.match(merge_request.target_branch):
                log.debug("MR does not match branch_regexp: %s", merge_request.web_url)
                continue

            if not source_branch_regexp.match(merge_request.source_branch):
                log.debug(
                    "MR does not match source_branch_regexp: %s", merge_request.web_url
                )
                continue

            project_merge_requests[project_id].append(merge_request)

        filtered_merge_requests = {}
        project_regexp = self._config.project_regexp
        for project_id, merge_requests in project_merge_requests.items():
            project = Project.fetch_by_id(project_id, self.api)

            if project.archived:
                log.debug("Project is archived: %s", project.path_with_namespace)
                continue

            if project_regexp.match(project.path_with_namespace):
                filtered_merge_requests[project] = merge_requests
            else:
                log.debug(
                    "Project does not match project_regexp: %s",
                    project.path_with_namespace,
                )

        return filtered_merge_requests

    def _process_merge_requests(
        self,
        repo_manager: store.RepoManager,
        project: Project,
        merge_requests: list[MergeRequest],
    ) -> None:
        if not merge_requests:
            log.info("Nothing to merge at this point...")
            return

        try:
            repo = repo_manager.repo_for_project(project)
        except git.GitError:
            log.exception("Couldn't initialize repository for project!")
            raise

        log.info("Got %s requests to merge;", len(merge_requests))
        if self._config.batch and len(merge_requests) > 1:
            log.info(
                "Attempting to merge as many MRs as possible using BatchMergeJob..."
            )
            batch_merge_job = batch_job.BatchMergeJob(
                api=self._api,
                user=self.user,
                project=project,
                merge_requests=merge_requests,
                repo=repo,
                options=self._config.merge_opts,
                batch_branch_name=self._config.batch_branch_name,
            )
            try:
                batch_merge_job.execute(exc_comment=self._config.exc_comment)
                return
            except batch_job.CannotBatch as err:
                log.warning("BatchMergeJob aborted: %s", err)
            except job.CannotMerge as err:
                log.warning("BatchMergeJob failed: %s", err)
                return
            except git.GitError as err:
                log.exception("BatchMergeJob failed: %s", err)
        log.info("Attempting to merge the oldest MR...")
        merge_request = merge_requests[0]
        merge_job = self._get_single_job(
            project=project,
            merge_request=merge_request,
            repo=repo,
            options=self._config.merge_opts,
        )
        merge_job.execute(exc_comment=self._config.exc_comment)

    def _get_single_job(
        self,
        project: Project,
        merge_request: MergeRequest,
        repo: git.Repo,
        options: job.MergeJobOptions,
    ) -> single_merge_job.SingleMergeJob:
        return single_merge_job.SingleMergeJob(
            api=self._api,
            user=self.user,
            project=project,
            merge_request=merge_request,
            repo=repo,
            options=options,
        )


@dataclasses.dataclass
class BotConfig:
    user: user_module.User
    use_https: bool
    auth_token: str
    ssh_key_file: Optional[str]
    project_regexp: "re.Pattern[str]"
    merge_order: str
    merge_opts: job.MergeJobOptions
    git_timeout: datetime.timedelta
    git_reference_repo: str
    branch_regexp: "re.Pattern[str]"
    source_branch_regexp: "re.Pattern[str]"
    batch: bool
    cli: bool
    batch_branch_name: str
    exc_comment: Optional[str]


MergeJobOptions = job.MergeJobOptions
Fusion = job.Fusion

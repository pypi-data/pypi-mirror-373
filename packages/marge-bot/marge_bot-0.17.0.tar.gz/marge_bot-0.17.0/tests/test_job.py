# pylint: disable=protected-access
import dataclasses
import textwrap
from datetime import timedelta
from unittest.mock import ANY, MagicMock, create_autospec, patch

import pytest

import marge.git
import marge.gitlab
import marge.interval
import marge.merge_request
import marge.project
import marge.user
from marge.hooks import run_hook
from marge.job import CannotMerge, Fusion, MergeJob, MergeJobOptions, SkipMerge


class TestJob:
    def _mock_merge_request(self, **options):
        return create_autospec(
            marge.merge_request.MergeRequest, spec_set=True, **options
        )

    def get_merge_job(self, **merge_kwargs):
        params = {
            "api": create_autospec(marge.gitlab.Api, spec_set=True),
            "user": create_autospec(marge.user.User, spec_set=True),
            "project": create_autospec(marge.project.Project, spec_set=True),
            "repo": create_autospec(marge.git.Repo, spec_set=True),
            "options": MergeJobOptions(),
        }
        params.update(merge_kwargs)
        return MergeJob(**params)

    def test_get_source_project_when_is_target_project(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request()
        merge_request.source_project_id = merge_job._project.id
        r_source_project = merge_job.get_source_project(merge_request)
        assert r_source_project is merge_job._project

    def test_get_source_project_when_is_fork(self):
        with patch("marge.job.Project") as project_class:
            merge_job = self.get_merge_job()
            merge_request = self._mock_merge_request()
            r_source_project = merge_job.get_source_project(merge_request)

            project_class.fetch_by_id.assert_called_once_with(
                merge_request.source_project_id, api=merge_job._api
            )
            assert r_source_project is not merge_job._project
            assert r_source_project is project_class.fetch_by_id.return_value

    def test_get_mr_ci_status(self):
        with patch("marge.job.Pipeline", autospec=True) as pipeline_class:
            pipeline_success = [MagicMock(sha="abc", status="success", id=12345)]
            pipeline_class.pipelines_by_branch.return_value = pipeline_success
            pipeline_class.pipelines_by_merge_request.return_value = pipeline_success
            merge_job = self.get_merge_job()
            merge_request = self._mock_merge_request(sha="abc")

            r_ci_status, _, r_pipeline_id = merge_job.get_mr_ci_status(merge_request)

            pipeline_class.pipelines_by_merge_request.assert_called_once_with(
                merge_request.target_project_id, merge_request.iid, merge_job._api
            )
            assert r_ci_status == "success"
            assert r_pipeline_id == 12345

    def test_ensure_mergeable_mr_not_assigned(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request(
            state="opened", draft=False, squash=False
        )
        with pytest.raises(SkipMerge) as exc_info:
            merge_job.ensure_mergeable_mr(merge_request)
        assert (
            exc_info.value.reason
            == "The MR is not assigned to Marge anymore. Please assign it back to Marge to merge."
        )

    def test_ensure_mergeable_mr_state_not_ok(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request(
            assignee_ids=[merge_job._user.id], state="merged", draft=False, squash=False
        )
        with pytest.raises(CannotMerge) as exc_info:
            merge_job.ensure_mergeable_mr(merge_request)
        assert exc_info.value.reason == "The merge request is already merged!"

    def test_ensure_mergeable_mr_not_approved(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request(
            assignee_ids=[merge_job._user.id], state="opened", draft=False, squash=False
        )
        merge_request.fetch_approvals.return_value.sufficient = False
        with pytest.raises(CannotMerge) as exc_info:
            merge_job.ensure_mergeable_mr(merge_request)

        merge_request.fetch_approvals.assert_called_once()
        assert "Insufficient approvals" in str(exc_info.value)

    def test_ensure_mergeable_mr_draft(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request(
            assignee_ids=[merge_job._user.id], state="opened", draft=True
        )
        merge_request.fetch_approvals.return_value.sufficient = True
        with pytest.raises(CannotMerge) as exc_info:
            merge_job.ensure_mergeable_mr(merge_request)

        assert exc_info.value.reason == (
            "It is not possible to merge MRs marked as Draft. "
            "Please undraft it before assigning to Marge next time."
        )

    def test_ensure_mergeable_mr_unresolved_discussion(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request(
            assignee_ids=[merge_job._user.id],
            state="opened",
            draft=False,
            blocking_discussions_resolved=False,
        )
        merge_request.fetch_approvals.return_value.sufficient = True
        with pytest.raises(CannotMerge) as exc_info:
            merge_job.ensure_mergeable_mr(merge_request)

        assert exc_info.value.reason == (
            "Merge requests which have unresolved discussions cannot be merged. "
            "Please address all feedback and mark discussions as resolved."
        )

    def test_ensure_mergeable_mr_squash_and_trailers(self):
        merge_job = self.get_merge_job(options=MergeJobOptions(add_reviewers=True))
        merge_request = self._mock_merge_request(
            assignee_ids=[merge_job._user.id], state="opened", draft=False, squash=True
        )
        merge_request.fetch_approvals.return_value.sufficient = True
        with pytest.raises(CannotMerge) as exc_info:
            merge_job.ensure_mergeable_mr(merge_request)

        assert exc_info.value.reason == (
            "Merging requests marked as auto-squash is not possible due to configuration. "
            "Please disable squashing or talk with the maintainers about the commit tagging config."
        )

    def test_unassign_from_mr(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request()

        # when we are not the author
        merge_job.unassign_from_mr(merge_request)
        merge_request.assign_to.assert_called_once_with(merge_request.author_id)

        # when we are the author
        merge_request.author_id = merge_job._user.id
        merge_job.unassign_from_mr(merge_request)
        merge_request.unassign.assert_called_once()

    def test_fuse_using_rebase(self):
        merge_job = self.get_merge_job(options=MergeJobOptions(fusion=Fusion.rebase))
        branch_a = "A"
        branch_b = "B"

        merge_job.fuse(branch_a, branch_b)

        merge_job._repo.rebase.assert_called_once_with(
            branch_a, branch_b, source_repo_url=ANY, local=ANY
        )

    def test_fuse_using_merge(self):
        merge_job = self.get_merge_job(options=MergeJobOptions(fusion=Fusion.merge))
        branch_a = "A"
        branch_b = "B"

        merge_job.fuse(branch_a, branch_b)

        merge_job._repo.merge.assert_called_once_with(
            branch_a, branch_b, source_repo_url=ANY, local=ANY
        )

    def test_pipeline_msg_hook_is_called(self, tmp_path):
        hooks_dir = tmp_path / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        hook_file = hooks_dir / "pipeline_message.py"

        hook_content = textwrap.dedent(
            """
        def main(pipeline_id, project_id):
            return "Hook executed for pipeline %s in project %s" % (pipeline_id, project_id)
        """
        )
        hook_file.write_text(hook_content, encoding="utf-8")

        pipeline_id = 123
        project_id = "hooks_project"
        hook_ret = run_hook(hooks_dir, "pipeline_message", pipeline_id, project_id)
        assert hook_ret is not None

        expected_result = (
            f"Hook executed for pipeline {pipeline_id} in project {project_id}"
        )
        assert hook_ret == expected_result

    def test_pipeline_msg_hook_no_file(self, tmp_path):
        hooks_dir = tmp_path / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        pipeline_id = 123
        project_id = "hooks_project"
        hook_ret = run_hook(hooks_dir, "no_such_hook", pipeline_id, project_id)
        assert hook_ret is None

    def test_raises_needs_rebase(self):
        merge_job = self.get_merge_job()
        merge_request = self._mock_merge_request(detailed_merge_status="need_rebase")

        with pytest.raises(marge.job.NeedsRebase) as exc_info:
            merge_job.wait_for_merge_status_to_resolve(merge_request)

        assert str(exc_info.value) == "MR needs to be rebased."


class TestMergeJobOptions:
    def test_default(self):
        assert MergeJobOptions() == MergeJobOptions(
            add_tested=False,
            add_part_of=False,
            add_reviewers=False,
            reapprove=False,
            approval_timeout=timedelta(seconds=0),
            embargo=marge.interval.IntervalUnion.empty(),
            ci_timeout=timedelta(minutes=15),
            fusion=Fusion.rebase,
            use_no_ff_batches=False,
            use_merge_commit_batches=False,
            skip_ci_batches=False,
            guarantee_final_pipeline=False,
            custom_allowed_approvers=None,
            custom_required_approvals=0,
        )

    def test_default_ci_time(self):
        three_min = timedelta(minutes=3)
        assert MergeJobOptions(ci_timeout=three_min) == dataclasses.replace(
            MergeJobOptions(), ci_timeout=three_min
        )

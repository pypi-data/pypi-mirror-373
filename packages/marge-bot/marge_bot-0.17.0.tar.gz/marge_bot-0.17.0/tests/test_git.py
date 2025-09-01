import dataclasses
import datetime
import os
import pathlib
import re
import shlex
import subprocess
from unittest import mock

import pytest

import marge.git
from marge import keepcommitters
from marge.git import GIT_SSH_COMMAND

GIT_CLONE_COMMAND = "git clone --origin=origin --filter=blob:none"


# pylint: disable=attribute-defined-outside-init
@mock.patch("marge.git._run")
class TestRepo:
    def setup_method(self, _method):
        self.repo = marge.git.Repo(
            remote_url="ssh://git@git.foo.com/some/repo.git",
            local_path="/tmp/local/path",
            user_name="bart",
            user_email="bart.simpson@gmail.com",
            ssh_key_file=None,
            timeout=datetime.timedelta(seconds=1),
            reference=None,
            keep_committers=False,
        )

    def test_clone(self, mocked_run):
        self.repo.clone()
        assert get_calls(mocked_run) == [
            f"{GIT_CLONE_COMMAND} ssh://git@git.foo.com/some/repo.git /tmp/local/path"
        ]

    def test_configure(self, mocked_run):
        self.repo.configure()
        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path config user.email bart.simpson@gmail.com",
            "git -C /tmp/local/path config user.name bart",
        ]

    def test_fetch(self, mocked_run):
        self.repo.fetch("source", "ssh://git@git.foo.com/forked/repo.git")
        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path remote rm source",
            "git -C /tmp/local/path remote add source ssh://git@git.foo.com/forked/repo.git",
            "git -C /tmp/local/path config remote.source.partialclonefilter blob:none",
            "git -C /tmp/local/path fetch --prune source",
        ]

    def test_rebase_success(self, mocked_run):
        self.repo.rebase("feature_branch", "master_of_the_universe")

        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path fetch --prune origin",
            "git -C /tmp/local/path checkout -B feature_branch origin/feature_branch --",
            "git -C /tmp/local/path rebase origin/master_of_the_universe",
            "git -C /tmp/local/path rev-parse HEAD",
        ]

    def test_merge_success(self, mocked_run):
        self.repo.merge("feature_branch", "master_of_the_universe")

        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path fetch --prune origin",
            "git -C /tmp/local/path checkout -B feature_branch origin/feature_branch --",
            "git -C /tmp/local/path merge origin/master_of_the_universe",
            "git -C /tmp/local/path rev-parse HEAD",
        ]

    def test_reviewer_tagging_success(self, mocked_run):
        self.repo.tag_with_trailer(
            trailer_name="Reviewed-by",
            trailer_values=["John Simon <john@invalid>"],
            branch="feature_branch",
            start_commit="origin/master_of_the_universe",
            keep_trailers=False,
        )

        rewrite, parse = get_calls(mocked_run)
        pattern = "".join(
            [
                "git -C /tmp/local/path filter-branch --force ",
                "--msg-filter.*John Simon <john@invalid>.*origin/master_of_the_universe..feature_branch",
            ]
        )
        assert re.match(pattern, rewrite)
        assert parse == "git -C /tmp/local/path rev-parse HEAD"

    def test_reviewer_tagging_failure(self, mocked_run):
        def fail_on_filter_branch(*args, **unused_kwargs):
            if "filter-branch" in args:
                raise subprocess.CalledProcessError(returncode=1, cmd="git rebase blah")
            if "rev-parse" in args or "reset" in args:
                return mock.Mock()
            raise NotImplementedError("Unexpected call:", args)

        mocked_run.side_effect = fail_on_filter_branch

        try:
            self.repo.tag_with_trailer(
                trailer_name="Reviewed-by",
                branch="feature_branch",
                start_commit="origin/master_of_the_universe",
                trailer_values=["John Simon <john@invalid.com>"],
                keep_trailers=False,
            )
        except marge.git.GitError:
            pass
        else:
            assert False
        rewrite, check, abort = get_calls(mocked_run)
        assert "filter-branch" in rewrite
        assert check == "git -C /tmp/local/path rev-parse refs/original/refs/heads/"
        assert (
            abort
            == "git -C /tmp/local/path reset --hard refs/original/refs/heads/feature_branch"
        )

    def test_sign_success(self, mocked_run):
        self.repo.sign_commits(
            branch="feature_branch", start_commit="origin/master_of_the_universe"
        )

        rewrite, parse = get_calls(mocked_run)
        pattern = "".join(
            [
                "git -C /tmp/local/path filter-branch --force ",
                "--commit-filter 'git commit-tree -S \\$@' ",
                "--env-filter "
                "'GIT_COMMITTER_EMAIL=bart.simpson@gmail.com "
                "GIT_COMMITTER_NAME=bart' ",
                "origin/master_of_the_universe..feature_branch",
            ]
        )
        assert re.match(pattern, rewrite)
        assert parse == "git -C /tmp/local/path rev-parse HEAD"

    def test_rebase_same_branch(self, mocked_run):
        with pytest.raises(AssertionError):
            self.repo.rebase("branch", "branch")

        assert get_calls(mocked_run) == []

    def test_merge_same_branch(self, mocked_run):
        with pytest.raises(AssertionError):
            self.repo.merge("branch", "branch")

        assert get_calls(mocked_run) == []

    def test_remove_branch(self, mocked_run):
        self.repo.remove_branch("some_branch", new_current_branch="devel")
        assert get_calls(mocked_run) == ["git -C /tmp/local/path branch -D some_branch"]

    def test_remove_branch_default(self, mocked_run):
        self.repo.remove_branch("some_branch")
        assert get_calls(mocked_run) == ["git -C /tmp/local/path branch -D some_branch"]

    def test_remove_master_branch_fails(self, unused_mocked_run):
        with pytest.raises(AssertionError):
            self.repo.remove_branch("meister", new_current_branch="meister")

    def test_push_force(self, mocked_run):
        mocked_run.return_value = mocked_stdout(b"")
        self.repo.push("my_branch", force=True)
        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path checkout my_branch --",
            "git -C /tmp/local/path diff-index --quiet HEAD",
            "git -C /tmp/local/path ls-files --others",
            "git -C /tmp/local/path push --force-with-lease origin my_branch:my_branch",
        ]

    def test_push_force_fails_on_dirty(self, mocked_run):
        def fail_on_diff_index(*args, **unused_kwargs):
            if "diff-index" in args:
                raise subprocess.CalledProcessError(
                    returncode=1, cmd="git diff-index blah"
                )

        mocked_run.side_effect = fail_on_diff_index

        with pytest.raises(marge.git.GitError):
            self.repo.push("my_branch", force=True)

        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path checkout my_branch --",
            "git -C /tmp/local/path diff-index --quiet HEAD",
        ]

    def test_push_force_fails_on_untracked(self, mocked_run):
        def fail_on_ls_files(*args, **unused_kwargs):
            if "ls-files" in args:
                return mocked_stdout("some_file.txt\nanother_file.py")
            return None

        mocked_run.side_effect = fail_on_ls_files

        with pytest.raises(marge.git.GitError):
            self.repo.push("my_branch", force=True)

        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path checkout my_branch --",
            "git -C /tmp/local/path diff-index --quiet HEAD",
            "git -C /tmp/local/path ls-files --others",
        ]

    def test_get_commit_hash(self, mocked_run):
        mocked_run.return_value = mocked_stdout(b"deadbeef")

        commit_hash = self.repo.get_commit_hash()
        assert commit_hash == "deadbeef"

        assert get_calls(mocked_run) == ["git -C /tmp/local/path rev-parse HEAD"]
        self.repo.get_commit_hash(rev="master")
        assert get_calls(mocked_run)[-1] == "git -C /tmp/local/path rev-parse master"

    def test_passes_ssh_key(self, mocked_run):
        repo = dataclasses.replace(self.repo, ssh_key_file="/foo/id_rsa")
        repo.configure()
        git_ssh = (
            f"GIT_SSH_COMMAND='{GIT_SSH_COMMAND} -F /dev/null -o IdentitiesOnly=yes -i "
            f"/foo/id_rsa'"
        )
        assert get_calls(mocked_run) == [
            f"{git_ssh} git -C /tmp/local/path config user.email bart.simpson@gmail.com",
            f"{git_ssh} git -C /tmp/local/path config user.name bart",
            f"{git_ssh} git -C /tmp/local/path config gpg.format ssh",
            f"{git_ssh} git -C /tmp/local/path config user.signingKey /foo/id_rsa",
        ]

    def test_passes_reference_repo(self, mocked_run):
        repo = dataclasses.replace(self.repo, reference="/foo/reference_repo")
        repo.clone()
        assert get_calls(mocked_run) == [
            f"{GIT_CLONE_COMMAND} --reference=/foo/reference_repo ssh://git@git.foo.com/some/repo.git "
            + "/tmp/local/path"
        ]

    def test_keep_committers(self, mocked_run):
        repo = dataclasses.replace(self.repo, keep_committers=True)
        repo.rebase("feature_branch", "master_of_the_universe")
        assert get_calls(mocked_run) == [
            "git -C /tmp/local/path fetch --prune origin",
            "git -C /tmp/local/path checkout -B feature_branch origin/feature_branch --",
            f"git -c 'rebase.instructionFormat=%s%nexec python3 {keepcommitters.__file__} "
            + "%H' -C /tmp/local/path rebase origin/master_of_the_universe",
            "git -C /tmp/local/path rev-parse HEAD",
        ]


def get_calls(mocked_run):
    return [bashify(call) for call in mocked_run.call_args_list]


def bashify(call):
    args, kwargs = call
    args = [shlex.quote(arg) for arg in args]
    env = kwargs.get("env") or {}
    default_env = os.environ.copy()
    default_env["FILTER_BRANCH_SQUELCH_WARNING"] = "1"
    alt_env = [
        shlex.quote(k) + "=" + shlex.quote(v)
        for k, v in set(env.items()) - set(default_env.items())
    ]
    return " ".join(alt_env + args)


def mocked_stdout(stdout):
    return subprocess.CompletedProcess(["blah", "args"], 0, stdout, None)


def _filter_test(message, trailer_name, trailer_values, keep_trailers):
    script = marge.git._filter_branch_script(  # pylint: disable=protected-access
        trailer_name, trailer_values, keep_trailers
    )
    result = subprocess.check_output(
        [b"sh", b"-c", script.encode("utf-8")],
        input=message.encode("utf-8"),
        stderr=subprocess.STDOUT,
    )
    return result.decode("utf-8")


def test_filter():
    assert _filter_test("Some Stuff", "Tested-by", [], False) == "Some Stuff\n"
    assert _filter_test("Some Stuff\n", "Tested-by", [], False) == "Some Stuff\n"
    assert (
        _filter_test(
            "Some Stuff", "Tested-by", ["T. Estes <testes@example.com>"], False
        )
        == """Some Stuff

Tested-by: T. Estes <testes@example.com>
"""
    )

    test_commit_message = r"""Fix: bug in BLah.

Some stuff.
Some More stuff (really? Yeah: really!)

Reviewed-by: R. Viewer <rviewer@example.com>
Reviewed-by: R. Viewer <rviewer@example.com>
Signed-off-by: Stephen Offer <soffer@example.com>
"""
    with_tested_by = _filter_test(
        test_commit_message, "Tested-by", ["T. Estes <testes@example.com>"], False
    )
    assert (
        with_tested_by
        == """Fix: bug in BLah.

Some stuff.
Some More stuff (really? Yeah: really!)

Reviewed-by: R. Viewer <rviewer@example.com>
Signed-off-by: Stephen Offer <soffer@example.com>
Tested-by: T. Estes <testes@example.com>
"""
    )
    with_new_reviewed_by = _filter_test(
        with_tested_by,
        "Reviewed-by",
        ["Roger Ebert <ebert@example.com>", "John Simon <simon@example.com>"],
        False,
    )
    assert (
        with_new_reviewed_by
        == """Fix: bug in BLah.

Some stuff.
Some More stuff (really? Yeah: really!)

Signed-off-by: Stephen Offer <soffer@example.com>
Tested-by: T. Estes <testes@example.com>
Reviewed-by: Roger Ebert <ebert@example.com>
Reviewed-by: John Simon <simon@example.com>
"""
    )
    with_keep_reviewed_by = _filter_test(
        with_tested_by,
        "Reviewed-by",
        ["Roger Ebert <ebert@example.com>", "John Simon <simon@example.com>"],
        True,
    )
    assert (
        with_keep_reviewed_by
        == """Fix: bug in BLah.

Some stuff.
Some More stuff (really? Yeah: really!)

Reviewed-by: R. Viewer <rviewer@example.com>
Signed-off-by: Stephen Offer <soffer@example.com>
Tested-by: T. Estes <testes@example.com>
Reviewed-by: Roger Ebert <ebert@example.com>
Reviewed-by: John Simon <simon@example.com>
"""
    )
    assert (
        _filter_test("Test: frobnificator", "Tested-by", [], False)
        == "Test: frobnificator\n"
    )
    assert _filter_test(
        "Test: frobnificator", "Tested-by", ["T. Estes <testes@example.com>"], False
    ) == (
        """Test: frobnificator

Tested-by: T. Estes <testes@example.com>
"""
    )


def test_filter_fails_on_empty_commit_messages():
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        _filter_test("", "", [], False)
    assert exc_info.value.output == b"ERROR: Expected a non-empty commit message"


def test_filter_fails_on_commit_messages_that_are_empty_apart_from_trailers():
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        _filter_test(
            "Tested-by: T. Estes <testes@example.com>",
            "Tested-by",
            ["T. Estes <testes@example.com>"],
            False,
        )
    assert exc_info.value.output == b"".join(
        [
            b"ERROR: Your commit message seems to consist only of ",
            b"Trailers: Tested-by: T. Estes <testes@example.com>",
        ]
    )

    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        _filter_test("", "Tested-by", ["T. Estes <testes@example.com>"], False)
    assert exc_info.value.output == b"ERROR: Expected a non-empty commit message"


def test_filter_ignore_first_line_trailer_in_commit_message_if_not_set():
    assert (
        _filter_test(
            "Tested-by: T. Estes <testes@example.com>",
            "Reviewed-by",
            ["John Simon <john@invalid>"],
            False,
        )
        == """Tested-by: T. Estes <testes@example.com>

Reviewed-by: John Simon <john@invalid>
"""
    )


def _commit_blob(repo, index):
    blob = pathlib.Path(repo.remote_url) / f"blob{index}"
    with blob.open("wb") as file:
        file.truncate(1024)
    repo.git("-C", repo.remote_url, "add", blob.name)
    repo.git("-C", repo.remote_url, "commit", "-m", f"Commit {index}", blob.name)


def test_blobless_rebase(_git_user_config, tmp_repo):
    """Test rebase against a "remote" repo and a local blobless checkout."""
    _commit_blob(tmp_repo, "1")
    _commit_blob(tmp_repo, "2a")
    tmp_repo.git("-C", tmp_repo.remote_url, "checkout", "-b", "feature", "HEAD~1")
    _commit_blob(tmp_repo, "2b")

    tmp_repo.clone()
    tmp_repo.rebase("feature", "main")

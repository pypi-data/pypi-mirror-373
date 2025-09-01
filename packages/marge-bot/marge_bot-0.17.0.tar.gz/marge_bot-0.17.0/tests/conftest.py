import datetime

import pytest

import marge


@pytest.fixture
def tmp_repo(tmp_path_factory):
    source = str(tmp_path_factory.mktemp("source"))
    repo = marge.git.Repo(
        remote_url=source,
        local_path=str(tmp_path_factory.mktemp("checkout")),
        user_name="",
        user_email="",
        ssh_key_file=None,
        timeout=datetime.timedelta(seconds=10),
        reference=None,
        keep_committers=False,
    )
    repo.git("init", "-b", "main", source)
    yield repo


@pytest.fixture
def _git_user_config(monkeypatch):
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Tester")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "tester@example.com")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Tester")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "tester@example.com")

# marge-bot

[![pipeline status](https://gitlab.com/marge-org/marge-bot/badges/main/pipeline.svg)](https://gitlab.com/marge-org/marge-bot/-/commits/main)
[![Latest Release](https://gitlab.com/marge-org/marge-bot/-/badges/release.svg)](https://gitlab.com/marge-org/marge-bot/-/releases)

**marge-bot** is a merge bot for advanced merge request workflows on GitLab.
Marge helps keep your main branch green, and comes with a set of features to make
managing merge requests at scale easier. It improves on GitHub's
[merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)
and GitLab's [merge train](https://docs.gitlab.com/ee/ci/pipelines/merge_trains.html)
workflows by automatically handling rebases and merges, batching merge requests, and more.

Marge-bot offers a simple workflow: when a merge request is ready, just
assign it to the marge-bot user, and let her do all the rebase-wait-retry for you. If
anything goes wrong (merge conflicts, tests that fail, etc.) she'll leave a
message on the merge request, so you'll get notified. Marge-bot can handle an
adversarial environment where some developers prefer to merge their own changes,
so the barrier for adoption is really low.

Whether marge-bot will or will not wait for pipeline to succeed depends on the value of
"Pipelines must succeed" setting in your project. It is available in all Gitlab
versions, and should not be a barrier.

Since she is at it, she can optionally provide some other goodies like tagging
of commits (e.g. `Reviewed-by: ...`) or preventing merges during certain hours.

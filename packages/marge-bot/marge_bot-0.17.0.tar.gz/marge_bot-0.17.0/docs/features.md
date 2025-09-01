# Features

Marge provides a number of features beyond the basic merge train workflow.

## Suggested workflow

1. Alice creates a new merge request and assigns Bob and Charlie as reviewers

2. Both review the code and after all issues they raise are resolved by Alice,
   they approve the merge request and assign it to `marge-bot` for merging.

3. Marge-bot rebases the latest target branch (typically master) into the
   merge-request branch and pushes it. Once the tests have passed and there is a
   sufficient number of approvals (if a minimal approvals limit has been set on
   the project), Marge-bot will merge (or rebase, depending on project settings)
   the merge request via the GitLab API. It can also add some headers to all
   commits in the merge request as described in the next section.

## Adding `Reviewed-by:`, `Tested:` and `Part-of:` to commit messages

Marge-bot supports automated addition of the following
two [standardized git commit trailers](https://www.kernel.org/doc/html/v4.11/process/submitting-patches.html#using-reported-by-tested-by-reviewed-by-suggested-by-and-fixes):
`Reviewed-by` and `Tested-by`. For the latter it uses `Marge Bot
<$MERGE_REQUEST_URL>` as a slight abuse of the convention (here `Marge Bot` is
the name of the `marge-bot` user in GitLab).

If you pass `--add-reviewers` and the list of approvers is non-empty and you
have enough approvers to meet the required approver count, Marge will add the
following header to each commit message and each reviewer as it rebases the
target branch into your PR branch:

```txt
Reviewed-by: A. Reviewer <a.reviewer@example.com>
```

All existing `Reviewed-by:` trailers on commits in the branch will be stripped,
unless you use `--keep-reviewers` option. This
feature requires marge to run with admin privileges due to a peculiarity of the
GitLab API: only admin users can obtain email addresses of other users, even
ones explicitly declared as public (strangely this limitation is particular to
email, Skype handles etc. are visible to everyone).

If you pass `--add-tested` the final commit message in a PR will be tagged with
`Tested-by: marge-bot <$MERGE_REQUEST_URL>` trailer. This can be very useful for
two reasons:

1. Seeing where stuff "came from" in a rebase-based workflow
2. Knowing that a commit has been tested, which is e.g. important for bisection
   so you can easily and automatically `git bisect --skip` untested commits.

Additionally, by using `--add-part-of`, all commit messages will be tagged with
a `Part-of: <$MERGE_REQUEST_URL>` trailer to the merge request on which they
were merged. This is useful, for example, to go from a commit shown in `git
blame` to the merge request on which it was introduced or to easily revert a all
commits introduced by a single Merge Request when using a fast-forward/rebase
based merge workflow.

## Impersonating approvers

If you want a full audit trail, you will configure GitLab
[require approvals](https://docs.gitlab.com/ee/user/project/merge_requests/merge_request_approvals.html#approvals-required)
for PRs and also turn on
[reset approvals on push](https://docs.gitlab.com/ee/user/project/merge_requests/merge_request_approvals.html#reset-approvals-on-push).
Unfortunately, since Marge-bot's flow is based on pushing to the source branch, this
means it will reset the approval status if the latter option is enabled.
However, if you have given Marge-bot admin privileges and turned on
`--impersonate-approvers`, she will re-approve the merge request assuming after its own
push, but by impersonating the existing approvers.

## Merge embargoes

Marge-bot can be configured not to merge during certain periods. E.g., to prevent
her from merging during weekends, add `--embargo 'Friday 6pm - Monday 9am'`.
This is useful for example if you automatically deploy from master and want to
prevent shipping late on a Friday, but still want to allow marking merge requests as
"to be merged on Monday": just assign them to `marge-bot` as any other day.

More than one embargo period can be specified, separated by commas. Any merge
request assigned to her during an embargo period, will be merged in only once all
embargoes are over.

## Batching Merge Requests

The flag `--batch` enables testing and merging merge requests in batches. This can
significantly speed up the rate at which marge-bot processes jobs - not just
because merge requests can be tested together, but because marge-bot will ensure
the whole set of merge requests is mergeable first. This includes, for example,
checking if a merge request is marked as Draft, or does not have enough approvals.
Essentially, users get faster feedback if there is an issue. Note that you
probably won't need this unless you have tens of merge requests a day (or
extremely slow CI).

### How it works

If marge-bot finds multiple merge requests to deal with, she attempts to create
a batch job. She filters the merge requests such that they have all have a
common target branch, and eliminates those that have not yet passed CI (a
heuristic to help guarantee the batch will pass CI later).

Once the merge requests have been gathered, a batch branch is created using the
commits from each merge request in sequence. Any merge request that cannot be
merged to this branch (e.g. due to a rebase conflict) is filtered out. A new
merge request is then created for this branch, and tested in CI.

If CI passes, the original merge requests will be merged one by one.

If the batch job fails for any reason, we fall back to merging the first merge
request, before attempting a new batch job.

### Limitations

* Currently we still add the tested-by trailer for each merge request's final
  commit in the batch, but it would probably be more correct to add the trailer
  only to the last commit in the whole batch request (since that's the only one
  we know passed for sure in that combination). We might change this in the
  future or make it configurable, but note that there's still a much stronger
  chance all intermittent final commits also passed then when just testing on
  each source branch, because we know the final linearization of all commits
  passes in that all MRs passed individually on their branches.

* As trailers are added to the original merge requests only, their branches
  would need to be pushed to in order to reflect this change. This would trigger
  CI in each of the branches again that would have to be passed before merging,
  which effectively defeats the point of batching. To workaround this, the
  current implementation merges to the target branch through git, instead of the
  GitLab API. GitLab will detect the merge request as having been merged, and
  update the merge request status accordingly, regardless of whether it has
  passed CI. This does still mean the triggered CI jobs will be running even
  though the merge requests are merged. marge-bot will attempt to cancel these
  pipelines, although this doesn't work too effectively if external CI is used.

* There is what can be considered to be a flaw in this implementation that could
  potentially result in a non-green master; consider the following situation:

  1. A batch merge request is created, and passes CI.
  2. Several merge requests are then merged to master, but one could fail
     (perhaps due to someone pushing directly to master in between).
  3. At this point, marge-bot will abort the batch job, resulting in a subset of
     the batch merge requests having been merged.

  We've guaranteed that individually, each of these merge requests pass CI, and
  together with some extra merge requests they also pass CI, but this does not
  guarantee that the subset will. However, this would only happen in a rather
  convoluted situation that can be considered to be very rare.

## Restricting the list of projects marge-bot considers

By default marge-bot will work on all projects that she is a member of.
Sometimes it is useful to restrict a specific instance of marge-bot to a subset
of projects. You can specify a regexp that projects must match (anchored at the
start of the string) with `--project-regexp`.

One use-case is if you want to use different configurations (e.g.
`--add-reviewers` on one project, but not the others). A simple way of doing is
run two instances of marge-bot passing `--add-reviewers --project-regexp
project/with_reviewers` to the first instance and `--project-regexp
(?!project/with_reviewers)` to the second ones. The latter regexp is a negative
look-ahead and will match any string not starting with `project/with_reviewers`.

## Restricting the list of branches marge-bot considers

It is also possible to restrict the branches marge-bot watches for incoming
merge requests. By default, marge-bot will process MRs targeted for any branch.
You may specify a regexp that target branches must match with `--branch-regexp`.

This could be useful, if for instance, you wanted to set a regular freeze
interval on your master branches for releases. You could have one instance of
marge-bot with `--embargo "Friday 1pm - Monday 9am" --branch-regexp master` and
the other with `--branch-regexp (?!master)`. This would allow development to
continue on other branches during the embargo on master.

It is possible to restrict the source branches with `--source-branch-regexp`.

## Some handy git aliases

Only `git bisect run` on commits that have passed CI (requires running marge-bot with `--add-tested`):

```sh
git config --global alias.bisect-run-tested \
 'f() { git bisect run /bin/sh -c "if !(git log -1 --format %B | fgrep -q \"Tested-by: Marge Bot\"); then exit 125; else "$@"; fi"; }; f'
```

E.g. `git bisect-run-tested ./test-for-some-bug.sh`.

Revert a whole MR, in a rebase based workflow (requires running marge-bot with `--add-part-of`):

```sh
git config --global alias.mr-revs '!f() { git log --grep "^Part-of.*/""$1"">" --pretty="%H"; }; f'
git config --global alias.mr-url '!f() { git log -1 --grep "^Part-of.*/""$1"">" --pretty="%b" | grep "^Part-of.*/""$1"">"  | sed "s/.*<\\(.*\\)>/\\1/"; }; f'
git config --global alias.revert-mr '!f() { REVS=$(git mr-revs "$1"); URL="$(git mr-url "$1")";  git revert --no-commit $REVS;  git commit -m "Revert <$URL>$(echo;echo; echo "$REVS" | xargs -I% echo "This reverts commit %.")"; }; f'
```

E.g. `git revert-mr 123`. This will create a single commit reverting all commits
that are part of MR 123 with a commit message that looks like this:

```txt
Revert <http://gitlab.example.com/mygropup/myproject/merge_requests/123>

This reverts commit 86a3d35d9bc12e735efbf72f3e2fb895c0158713.
This reverts commit e862330a6df463e36137664f316c18b5836a4df7.
This reverts commit 0af5b70a98858c9509c895da2a673ebdb31e20b1.
```

E.g. `git revert-mr 123`.

## Customizing Marge's Comments on Pipelines

Marge-bot waits for the latest pipeline to succeed when a project requires the pipeline to pass before merging. If the pipeline fails, is canceled, or times out, marge-bot will comment on the merge request to explain why it couldn't be merged. You can customize marge-bot's comments to suit your project by writing a `pipeline_message.py` script and using the `--hooks-directory` option to provide the absolute path to the directory containing the script.

For example, if the absolute path of your script is `/shared/.marge/hooks/pipeline_message.py`, then run marge-bot with `--hooks-directory /shared/.marge/hooks`.

The pipeline message hook:
   * Must be named `pipeline_message.py`.
   * Must accept two arguments: `pipeline_id: str, project_id: str`.
   * Must return a markdown-formatted string which marge-bot will add to the pipeline message.

# Configuring marge-bot

Args that start with '--' (eg. `--auth-token`) can also be set in a config file
(specified via `--config-file`). The config file uses YAML syntax and must
represent a YAML 'mapping' (for details, see
<http://learn.getgrav.org/advanced/yaml>). If an arg is specified in more than one
place, then commandline values override environment variables which override
config file values which override defaults.

<!--
Editor note: To update the text below,
copy and paste from the output of
    uv run marge --help
-->

```txt
options:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        Config file path.
                           [env var: MARGE_CONFIG_FILE] (default: None)
  --auth-token TOKEN    Your GitLab token.
                        DISABLED because passing credentials on the command line is insecure:
                        You can still set it via ENV variable or config file, or use "--auth-token-file" flag.
                           [env var: MARGE_AUTH_TOKEN] (default: None)
  --auth-token-file FILE
                        Path to your GitLab token file.
                           [env var: MARGE_AUTH_TOKEN_FILE] (default: None)
  --gitlab-url URL      Your GitLab instance, e.g. "https://gitlab.example.com".
                           [env var: MARGE_GITLAB_URL] (default: None)
  --use-https           Use HTTP(S) instead of SSH for GIT repository access.
                           [env var: MARGE_USE_HTTPS] (default: False)
  --ssh-key KEY         The private ssh key for marge so it can clone/push.
                        DISABLED because passing credentials on the command line is insecure:
                        You can still set it via ENV variable or config file, or use "--ssh-key-file" flag.
                           [env var: MARGE_SSH_KEY] (default: None)
  --ssh-key-file FILE   Path to the private ssh key for marge so it can clone/push.
                           [env var: MARGE_SSH_KEY_FILE] (default: None)
  --embargo INTERVAL[,..]
                        Time(s) during which no merging is to take place, e.g. "Friday 1pm - Monday 9am".
                           [env var: MARGE_EMBARGO] (default: None)
  --use-merge-strategy  Use git merge instead of git rebase to update the *source* branch (EXPERIMENTAL)
                        If you need to use a strict no-rebase workflow (in most cases
                        you don't want this, even if you configured gitlab to use merge requests
                        to use merge commits on the *target* branch (the default).)
                           [env var: MARGE_USE_MERGE_STRATEGY] (default: False)
  --rebase-remotely     Instead of rebasing in a local clone of the repository, use GitLab's
                        built-in rebase functionality, via their API. Note that Marge can't add
                        information in the commits in this case.
                           [env var: MARGE_REBASE_REMOTELY] (default: False)
  --sign-commits        Sign commits with the same SSH key used to authenticate.
                           [env var: MARGE_SIGN_COMMITS] (default: False)
  --add-tested          Add "Tested: marge-bot <$MR_URL>" for the final commit on branch after it passed CI.
                           [env var: MARGE_ADD_TESTED] (default: False)
  --batch               Enable processing MRs in batches.
                           [env var: MARGE_BATCH] (default: False)
  --add-part-of         Add "Part-of: <$MR_URL>" to each commit in MR.
                           [env var: MARGE_ADD_PART_OF] (default: False)
  --batch-branch-name BATCH_BRANCH_NAME
                        Branch name when batching is enabled.
                           [env var: MARGE_BATCH_BRANCH_NAME] (default: marge_bot_batch_merge_job)
  --add-reviewers       Add "Reviewed-by: $approver" for each approver of MR to each commit in MR.
                           [env var: MARGE_ADD_REVIEWERS] (default: False)
  --keep-committers     Keep the original commit info during rebases.
                           [env var: MARGE_KEEP_COMMITTERS] (default: False)
  --keep-reviewers      Ensure previous "Reviewed-by: $approver" aren't dropped by --add-reviewers
                           [env var: MARGE_KEEP_REVIEWERS] (default: False)
  --impersonate-approvers
                        Marge-bot pushes effectively don't change approval status.
                           [env var: MARGE_IMPERSONATE_APPROVERS] (default: False)
  --merge-order {created_at,updated_at,assigned_at}
                        Order marge merges assigned requests. created_at (default), updated_at or assigned_at.
                           [env var: MARGE_MERGE_ORDER] (default: created_at)
  --approval-reset-timeout APPROVAL_RESET_TIMEOUT
                        How long to wait for approvals to reset after pushing.
                        Only useful with the "new commits remove all approvals" option in a project's settings.
                        This is to handle the potential race condition where approvals don't reset in GitLab
                        after a force push due to slow processing of the event.
                           [env var: MARGE_APPROVAL_RESET_TIMEOUT] (default: 0s)
  --project-regexp PROJECT_REGEXP
                        Only process projects that match; e.g. 'some_group/.*' or '(?!exclude/me)'.
                           [env var: MARGE_PROJECT_REGEXP] (default: .*)
  --ci-timeout CI_TIMEOUT
                        How long to wait for CI to pass.
                           [env var: MARGE_CI_TIMEOUT] (default: 15min)
  --max-ci-time-in-minutes MAX_CI_TIME_IN_MINUTES
                        Deprecated; use --ci-timeout.
                           [env var: MARGE_MAX_CI_TIME_IN_MINUTES] (default: None)
  --git-timeout GIT_TIMEOUT
                        How long a single git operation can take.
                           [env var: MARGE_GIT_TIMEOUT] (default: 120s)
  --git-reference-repo GIT_REFERENCE_REPO
                        A reference repo to be used when git cloning.
                           [env var: MARGE_GIT_REFERENCE_REPO] (default: None)
  --branch-regexp BRANCH_REGEXP
                        Only process MRs whose target branches match the given regular expression.
                           [env var: MARGE_BRANCH_REGEXP] (default: .*)
  --source-branch-regexp SOURCE_BRANCH_REGEXP
                        Only process MRs whose source branches match the given regular expression.
                           [env var: MARGE_SOURCE_BRANCH_REGEXP] (default: .*)
  --debug               Debug logging (includes all HTTP requests etc).
                           [env var: MARGE_DEBUG] (default: False)
  --run-manual-jobs     Add this flag to have Marge run on manual jobs within the pipeline.
                           [env var: MARGE_RUN_MANUAL_JOBS] (default: False)
  --use-no-ff-batches   Disable fast forwarding when merging MR batches.
                           [env var: MARGE_USE_NO_FF_BATCHES] (default: False)
  --use-merge-commit-batches
                        Use merge commit when creating batches, so that the commits in the batch MR
                        will be the same with in individual MRs. Requires sudo scope in the access token.
                           [env var: MARGE_USE_MERGE_COMMIT_BATCHES] (default: False)
  --skip-ci-batches     Skip CI when updating individual MRs when using batches.
                           [env var: MARGE_SKIP_CI_BATCHES] (default: False)
  --cli                 Run marge-bot as a single CLI command, not a service.
                           [env var: MARGE_CLI] (default: False)
  --guarantee-final-pipeline
                        Guaranteed final pipeline when assigned to marge-bot.
                           [env var: MARGE_GUARANTEE_FINAL_PIPELINE] (default: False)
  --exc-comment EXC_COMMENT
                        Provide additional text, like a log URL, to append to some exception-related MR comments.
                           [env var: MARGE_EXC_COMMENT] (default: None)
  --custom-approver [CUSTOM_APPROVER ...]
                        Specify one or more approver usernames to accept instead of asking GitLab.
                        For CE approval use.
                           [env var: MARGE_CUSTOM_APPROVER] (default: None)
  --custom-approvals-required CUSTOM_APPROVALS_REQUIRED
                        Required number of approvals from --custom-approval.
                        For CE approval use.
                           [env var: MARGE_CUSTOM_APPROVALS_REQUIRED] (default: 0)
  --hooks-directory HOOKS_DIRECTORY
                        Path to the directory where your custom hooks are located.
                           [env var: MARGE_HOOKS_DIRECTORY] (default: None)
```

Here is a config file example

```yaml
add-part-of: true
add-reviewers: true
keep-reviewers: false
add-tested: true
# choose one way of specifying the Auth token
#auth-token: TOKEN
auth-token-file: token.FILE
branch-regexp: .*
ci-timeout: 15min
embargo: Friday 1pm - Monday 9am
batch: false
git-timeout: 120s
gitlab-url: "https://gitlab.example.com"
impersonate-approvers: true
project-regexp: .*
# choose one way of specifying the SSH key
#ssh-key: KEY
ssh-key-file: token.FILE
# OR use HTTPS instead of SSH
#use-https: true
```

For more information about configuring marge-bot see `--help`.

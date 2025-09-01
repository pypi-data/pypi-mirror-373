
# Getting Started

First, create a user for marge-bot on your GitLab instance. We'll use `marge-bot` as
username here as well. GitLab sorts users by Name, so we recommend you pick one
that starts with a space, e.g. ` Marge Bot`, so it is quicker to assign to (our
code strips trailing whitespace in the name, so it won't show up elsewhere).
Then add `marge-bot` to your projects as `Developer` or `Maintainer`, the latter
being required if she will merge to protected branches.

For certain features, namely, `--impersonate-approvers`, and `--add-reviewers`,
you will need to grant `marge-bot` admin privileges as well. In the latter, so
that she can query the email of the reviewers to include it in the commit. Note
that if you're trying to run marge-bot against a GitLab instance you don't have
yourself admin access to (e.g. <https://www.gitlab.com>), you won't be able to use
features that require admin for marge-bot.

Second, you need an authentication token for the `marge-bot` user. You will need
to select the `api` and `read_user` scopes in all cases.

If marge-bot was made an admin to handle approver impersonation and/or adding a
reviewed-by field, then you will also need to add **`sudo`** scope under
`Impersonation Tokens` in the User Settings. Assuming your GitLab install is
install is `https://your-gitlab.example.com` the link will be at
`https://your-gitlab.example.com/admin/users/marge-bot/impersonation_tokens`.

On older GitLab installs, to be able to use impersonation features if marge-bot
was made an admin, use the **PRIVATE TOKEN** found in marge-bot's `Profile
Settings`; otherwise just use a personal token (you will need to impersonate the
marge-bot user via the admin UI to get the private token, it should then be at
`http://my-gitlab.example.com/profile/personal_access_tokens` reachable via
`Profile Settings -> Access Tokens`).

Once you have the token, put it in a file, e.g. `marge-bot.token`.

Finally, create a new ssh key-pair, e.g like so

```bash
ssh-keygen -t ed25519 -C marge-bot@invalid -f marge-bot-ssh-key -P ''
```

Add the public key (`marge-bot-ssh-key.pub`) to the user's `SSH Keys` in GitLab
and keep the private one handy.

Once you've set up the user, [configure](configuration.md) the options to your liking
and choose one of the [deployment options](run.md) to start running.

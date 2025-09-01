# Troubleshooting

Marge-bot continuously logs what she is doing, so this is a good place to look
in case of issues. In addition, by passing the `--debug` flag, additional info
such as REST requests and responses will be logged. When opening an issue,
please include a relevant section of the log, ideally ran with `--debug` enabled.

The most common source of issues is the presence of git-hooks that reject
Marge-bot as a committer. These may have been explicitly installed by someone in
your organization or they may come from the project configuration. E.g., if you
are using `Settings -> Repository -> Commit author's email`, you may need to
whitelist `marge-bot`'s email.

Some versions of GitLab are not good at reporting merge failures due to hooks
(the REST API may even claim the merge operation succeeded), you can find
this in `gitlab-rails/githost.log`, under GitLab's logs directory.

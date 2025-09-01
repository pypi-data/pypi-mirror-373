# Running marge-bot

Marge can be deployed in a number of ways that best suit your needs, from running the Python
app natively, to Docker, Kubernetes, or simple self-contained CI schedules.

## Running in Docker using SSH

!!! note
    Official, tagged images of the community fork are not yet deployed. You can
    try out the latest development images at `registry.gitlab.com/marge-org/marge-bot:main`.
    After the first release, tagged and `:latest` images will also become available.

Assuming you have already got docker installed, the quickest and most minimal
way to run marge is like so (*but see note about passing secrets on the
commandline below*):

```bash
docker run --restart=on-failure \ # restart if marge crashes because GitLab is flaky
  -e MARGE_AUTH_TOKEN="$(cat marge-bot.token)" \
  -e MARGE_SSH_KEY="$(cat marge-bot-ssh-key)" \
  registry.gitlab.com/marge-org/marge-bot:main \
  --gitlab-url='http://your.gitlab.instance.com'
```

Note that other users on the machine can see the secrets in `ps`, because
although they are env vars *inside* docker, we used a commandline switch to set
them for docker run.

To avoid that you have several options. You can just use a yaml file and mount
that into the container, for example this is how we actually run marge-bot at
Smarkets ourselves:

```yaml
# marge-bot-config.yml
add-part-of: true
add-reviewers: true
add-tested: true
impersonate-approvers: true
gitlab-url: "https://git.corp.smarkets.com"
project-regexp: "smarkets/smarkets$"
auth-token: "WoNtTelly0u"
ssh-key: |
    -----BEGIN OPENSSH PRIVATE KEY-----
    [...]
    -----END OPENSSH PRIVATE KEY-----
```

```bash
docker run --restart=on-failure \
  -v "$(pwd)":/configuration \
  registry.gitlab.com/marge-org/marge-bot:main \
  --config-file=/configuration/marge-bot-config.yaml
```

By default docker will use the `latest` tag, which corresponds to the latest
stable version. You can also use the `stable` tag to make this more explicit.
If you want a development version, you can use the `master` tag to obtain an
image built from the HEAD commit of the `master` branch. Note that this image
may contain bugs.

The marge-bot docker image is a [multi-platform image](https://docs.docker.com/build/building/multi-platform/),
so you can run it on amd64 and arm64 architectures.

You can also specify a particular version as a tag, e.g.
`registry.gitlab.com/marge-org/marge-bot:0.11.0`.

## Running in Docker Using HTTPS

It is also possible to use Git over HTTPS instead of Git over SSH. To use HTTPS instead of SSH,
add the `--use-https` flag and do not provide any SSH keys. Alternatively you can set the
environment variable `MARGE_USE_HTTPS` or the config file property `use-https`.

```bash
docker run --restart=on-failure \ # restart if marge crashes because GitLab is flaky
  -e MARGE_AUTH_TOKEN="$(cat marge-bot.token)" \
  registry.gitlab.com/marge-org/marge-bot:main \
  --use-https \
  --gitlab-url='http://your.gitlab.instance.com'
```

HTTPS can be used using any other deployment technique as well.

## Running in GitLab CI

You can also run marge-bot directly in your existing CI via scheduled pipelines
if you'd like to avoid setting up any additional infrastructure.

This way, you can inject secrets for marge-bot's credentials at runtime
inside the ephemeral container for each run by adding them to protected CI/CD
variables in a dedicated marge-bot runner project, as well as store execution
logs as artifacts for evidence.

You can also configure multiple setups in different CI schedules by supplying
`MARGE_*` environment variables per-schedule, such as running a different set
of projects or settings at different times.

Note that in this case, marge-bot will be slower than when run as a service,
depending on the frequency of your pipeline schedules.

Create a marge-bot runner project, and add the variables `MARGE_AUTH_TOKEN`
(of type Variable) and `MARGE_SSH_KEY_FILE` (of type File) in your CI/CD
Variables settings.

Then add a scheduled pipeline run to your project with the following minimal
`.gitlab-ci.yml` config:

```yaml
run:
  image:
    name: registry.gitlab.com/marge-org/marge-bot:main
    entrypoint: [""]
  only:
    - schedules
  variables:
    MARGE_CLI: "true"
    MARGE_GITLAB_URL: "$CI_SERVER_URL"
  script: marge.app
```

## Installing the Python package

You can also install Marge as a plain Python package (requires python3.9+):

```bash
# Install from remote 
pip install marge-bot

# Or install directly from the Git repository
pip install git+https://gitlab.com/marge-org/marge-bot.git#egg=marge

# Or run it straight from a local repository
git clone https://gitlab.com/marge-org/marge-bot.git
cd marge-bot/
pip install --editable .
```

Afterwards, the minimal way to run marge is as follows:

```bash
marge --auth-token-file marge-bot.token \
          --gitlab-url 'http://your.gitlab.instance.com' \
          --ssh-key-file marge-bot-ssh-key
```

However, we suggest you use a systemd unit file or some other mechanism to
automatically restart marge-bot in case of intermittent GitLab problems.

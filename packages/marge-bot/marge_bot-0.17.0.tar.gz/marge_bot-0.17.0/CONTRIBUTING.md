# Contributing to marge-bot

marge-bot is a community project and contributions are more than welcome to keep the project going.
Below are some basic guidelines to help you get started.

## Development environment

This project uses [uv](https://docs.astral.sh/uv/) for managing the virtual environment and
dependencies.

After checking out the repository, use `uv sync` to set up the virtual environment and
install all dependencies.

```bash session
git clone git@gitlab.com:marge-org/marge-bot.git
cd marge-bot
uv sync --group dev
```

### VS Code

Open the project in VS Code, let VS Code install the recommended extensions, and make sure to
select the Python virtual environment that Poetry created as the Python interpreter for the
project.

A `Marge` Run/Debug target is available out of the box. The target assumes that a
`development-config.yaml` file exists in the root of the repository.

## Commit messages

We use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification to format all our commit messages.
As a community-maintained project without a dedicated release management team, this helps us automate our releases
and changelog generation.

Commit formats are enforced using [commitizen](https://commitizen-tools.github.io/commitizen/) in our merge request pipelines. Please make sure your commit messages match this format and [amend your commit message](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/changing-a-commit-message) if the
commit lint step fails.

Below are a few examples of commits that would fail or pass our checks:

* Bad: `Added support for batching`
* Good: `feat(api): add support for batching merge requests`
* Bad: `Update documentation for batch jobs`
* Good: `docs(projects): update example for batch jobs`

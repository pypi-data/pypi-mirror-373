# DataRobot Python Client

[datarobot](https://pypi.org/project/datarobot/) is a Python library for working with the
[DataRobot](!http://datarobot.com) platform API.

This README is primarily intended for those developing the client. There is
also documentation intended for users of the client contained in the `docs`
directory of this repository. You can view the public documentation at
<https://docs.datarobot.com/en/docs/api/reference/sdk/>.

## Topics

* Development:
  * [Getting Started](#getting-started)
  * [Guidelines](#guidelines)
  * [Setup datarobot sdk locally](#installation)
  * [Running tests](#running-tests)
  * [Linting](#linting)
* Setup topics:
  * [Common DataRobot Client setup](#datarobot-client-setup)
    * [Setup with cfg file](#setup-with-cfg-file)
    * [Setup explicitly in code](#setup-explicitly-in-code)
    * [Setup with environment variables](#setup-with-environment-variables)
* Building the documentation

## Getting Started

You need to have

* Git
* Docker
* Python >= 3.11
* DataRobot account
* pip

While we require Python 3.11+ for development, we target Python 3.7 as well. We recommend using a
virtualenv to keep dependencies from conflicting with projects you may have on your machine.

## Guidelines

Our full list of suggestions and guidelines for code being added to this repository can be found [here](GUIDELINES.md).

## Installation

```console
git clone git@github.com:datarobot/public_api_client.git
cd public_api_client
# mkvirtualenv -p 3.11 ...
make req  # upgrades pip, setuptools, installs dev requirements
```

Note: This may have to be run as `root` or with `--user` flag if you are not
using python virtual environment.

## Build the documentation

Docker env:

```console
make clean test-docs
```

Local virtual env:

> Be sure to install pandoc before building documentation. Available via `apt-get` and `brew`

DataRobot has extensive documentation, which you can build locally for your
own reference. Before running the following build commands, please make sure that your
[public_api_client configuration](setup/getting_started.rst#use-a-configuration-file)
is present and valid or you have set the
[correct environment variables](setup/getting_started.rst#set-credentials-using-environment-variables).
Otherwise building the docs will take a lot of time.

```console
cd sdk_docs
make clean html
```

The documentation will then be built in a subdirectory, and can be viewed with
your web browser.

Alternatively, see <https://datarobot.atlassian.net/wiki/spaces/AIAPI/pages/28967932/Release+Tracker>
for pre-built documentation for the current cloud release and all enterprise
releases, as well as guidance on which version of the API goes with which
enterprise release.

To build a PDF of the docs for release:

```console
cd sdk_docs
make clean xelatexpdf
```

### Documentation Transition

As of 2024 Nov, we are transitioning the pySDK documentation from ReStructuredText (RST) to Markedly Structured Text (MyST). Practically, this means that our doc sources will be converted from `.rst` to `.md` files. This will allow us to more easily integrate PySDK docs with the rest of the DataRobot documentation in the [Docs Portal](https://docs.datarobot.com/). The `.rst` files will be removed once the transition is complete.

In order to perform this transition, we're added two dependencies, `myst-parser` and `rst-to-myst[sphinx]`. The first one is a parser for markdown and the second one is a converter from `.rst` to `.md`. However, these two dependencies are not compatible with each other, so we need to install them in separate environments. To do so, we have two make targets:

```console
make req
```

Which is the standard make target for creating a development environment, includes `myst-parser` and `sphinx` dependencies.

```console
make req-docs-transition
```

Includes `rst-to-myst[sphinx]` and its dependencies. This should be created in its own Python 3.11 environment, in order to avoid conflicts with the other dependencies, and to allow switching between environments to transition the old docs to markdown, then generate the Sphinx docs when needed.

**If you are writing new documentation we recommend you use MyST and write `.md` files. Anything in the sdk_docs folder will be automatically picked up and rendered as part of <https://datarobot-public-api-client.readthedocs-hosted.com/en/latest-release/> and, in turn, <https://docs.datarobot.com/en/docs/api/reference/sdk/>.

### DataRobot Client Setup

There are three different ways to set up the client to authenticate with the
server: through a config file, through environment variables, or explicitly in
the code.

You must specify an endpoint and an API token.  You can manage your API tokens in the DataRobot
webapp, in your profile.  If you access the DataRobot webapp at `https://app.datarobot.com`, then
the correct endpoint to specify would be `https://app.datarobot.com/api/v2`.

#### Setup with cfg file

The client will look for a config file `~/.config/datarobot/drconfig.yaml` by default. You can also
change that default to look for a config file at a different
path by using the using environment variable `DATAROBOT_CONFIG_FILE`.  Note that if you specify a
filepath it should be an absolute path so that the API client will work when run from any location.

This is an example of what that config file should look like.

```file
token: your_token
endpoint: https://app.datarobot.com/api/v2
```

#### Setup explicitly in code

Explicitly set up in code using your token, generated in Developer Tools:

```python
import datarobot as dr
dr.Client(token='your_token', endpoint='https://app.datarobot.com/api/v2')
```

Explicitly set up in code using your DataRobot OAuth2 token:

```python
# You can specify Authorization token type. "Token" is default value
dr.Client(token='your_oauth2_token', token_type="Bearer", endpoint='https://app.datarobot.com/api/v2')
```

You can also specify the location of a YAML config file to use:

```python
import datarobot as dr
dr.Client(config_path='/home/user/my_datarobot_config.yaml')
```

#### Setup with environment variables

Setup endpoint from environment variables in UNIX shell:

```shell
export DATAROBOT_API_TOKEN='MY_TOKEN'
export DATAROBOT_ENDPOINT='https://app.datarobot.com/api/v2'
```

## Running tests

If you don't have Python 3 installed, you can use docker to run Python 3 tests (runs 3.7 by default):

```console
make test-docker-py3
```

If you just want to run py.test against your system Python, run

```console
make test-pytest
```

The `test-pytest` and `test-docker-py3` targets support additional _make_ options. If you
need to pass specific flags to py.test, you can define them in the `PYTEST_OPTS` make
variable.

```console
make PYTEST_OPTS="--runxfail -vv" test-pytest
```

If you find yourself using these flags often, you can set an environment variable. For
simplicity, you can also define the `COVERAGE` variable which will generate a coverage
report in `htmlcov/index.html`.

```console
make COVERAGE=1 test-pytest
```

## Linting

You can use the following ``make`` commands to run linting (isort, black, mypy, ruff, pylint) against this repo:

* ``make ruff``: This runs [ruff](https://pypi.org/project/ruff/) checks against all files in the repo.
* ``make black-quick``: This runs black against only the files you've changed compared to master.
* ``make black``: This runs [black](https://pypi.org/project/black/) against all files in the repo.
* ``make check-isort``: This runs [isort](https://pypi.org/project/isort/) checks against all files in the repo.
* ``make flake``: This is a temporary alias for ``make ruff``.
* ``make pylint``: This runs [pylint](https://pypi.org/project/pylint/) checks against the repo.'s `datarobot` and `tests` directories
* ``make mypy``: This runs [mypy](https://pypi.org/project/mypy/) checks against a subset of the python files - see [pyproject.toml](pyproject.toml) for more information.
* ``make lint``: This runs all the linters checks against the repo: check-isort, mypy, check-black, flake, pylint

## Type Annotations

As you contribute to the repo, consider adding type annotations. See [DSX-2322](https://datarobot.atlassian.net/browse/DSX-2322) for more information, but:

1. Prefer `from __future__ import annotations` (PEP 563) to postpone annotation evaluation, rather than explicit string literals.
2. If you have updated an entire file, please remove it from `[tool.mypy.overrides]` in `pyproject.toml`.

If you have questions, please contact CFX.

## Copyright Notices

For legal purposes, we must protect this repo under the DataRobot Tool and Utility Agreement. To help automate this, you can use the following ``make commands`` to check and fix licenses. You will need to have Docker installed.

* ``make check-licenses``
* ``make fix-licenses``

Configuration of this tool can be found in [.licenserc.yaml](.licenserc.yaml).

## Development workflow tips and release process

Code going into the public api client is expected to be production-ready, "GA" quality. Two important
exceptions exist:

1. Client code may be needed for MBTesting during feature development; this should go in the `dev-internal`
   branch. It will be included in an _internally distributed_ package called `datarobot-internal`.
2. Client code may be useful for working with features at "preview" or "beta" maturity; this can go in
   the `master` branch in the directory `datarobot/_experimental`. Code in this directory will be included in an _externally distributed_
   package called [`datarobot-early-access`](https://pypi.org/project/datarobot-early-access/), but not included in the mainline (stable) package `datarobot`.
   Please think carefully if you really need to do this workflow, and coordinate with your domain PM.
3. Client code may need to be backported to older releases. If you need this, don't forget to open PRs
   against older release branches (`release/11.1`, `v3.7`, etc.). If it is critical to make a patch release of the client, open a CFX ticket
   in JIRA so that @datarobot/cfx can schedule it. `jarvis cherry-pick` is your friend.

For further details, please see this page on Confluence:
 [README supplement](https://datarobot.atlassian.net/wiki/spaces/CA/pages/2953740620/README+supplement+for+public+api+client+repo)

## Troubleshooting

Below are some potential issues users encounter when working with the DataRobot Python Client and their solutions.

### Can't Run Tests After Transitioning to ARM Machine

If you're transitioning from working on an x64 machine to an ARM-based machine, you may encounter errors
when trying to run tests locally. Errors include:

* `error: command 'cmake' failed: No such file or directory: 'cmake'`
* `error: command '/opt/homebrew/bin/cmake' failed with exit code 1`

To resolve this issue, update your development environment to a later version of python. As of December 2024, the SDK supports Python 3.7 - 3.13.
You can set the Python version when creating a virtual environment by running the following command: `mkvirtualenv sdk_3_11 --python 3.11`

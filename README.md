<a id="readme-top"></a>

<div align='center'>

[![Issues][issues-shield]][issues-url]

</div>
<br />
<h1 align="center">.github</h1>

## About The Project

A sensible set of standard workflows and associated files for reuse in all UKKA repos. The templates are a starting point and allow for customisation where a project is outside the bounds of what is normal.

## Conventional Commits

A lot of the workflows in this repo rely on the use of conventional commits. Check out the following documentation

- [**Conventional commits**](https://www.conventionalcommits.org/en/v1.0.0/)
- [**Conventional commits for VSCode**](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits)
  <br />

## Squash and Merge

Conventional commits go hand in hand with the squash and merge and the workflows here also expect that to be the merging strategy.

- [**Squash and merge**](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#squash-and-merge-your-commits)

## Usage

For public repos you can add the workflow templates via the actions tab.

- [**Choosing and using a workflow template**](https://docs.github.com/en/actions/how-tos/write-workflows/use-workflow-templates#choosing-and-using-a-workflow-template)

You can also copy and paste the templates into any repo you wish without the need to use the github UI.

## Available Workflows Templates

- <a href="#python_test">**UKKA Python Test**</a>
- <a href="#python_release">**UKKA Release**</a>
- <a href="#python_publish">**UKKA Publish**</a>
- <a href="#todo_check">**UKKA TODO Checker**</a>
- <a href="#file_check">**UKKA Python File Checker**</a>
- <a href="#pr_title">**UKKA Conventional PR Title**</a>
- <a href="#auto_pr">**UKKA Auto Pull Requests**</a>

<a id="python_test"></a>

## UKKA Python Test

Runs test commands in Python, with options to run across multiple OS, python versions and user defined package management system. Runs on PRs to the default branch.

**Consumed actions**: 
- [**actions/checkout**](https://github.com/actions/checkout)
- [**actions/setup-python**](https://github.com/actions/setup-python)

<br />

**Example Options**

```yaml
with:
      python_versions: '["3.10", "3.11"]'
        # Description: Python versions to test under 
        # Default: current lowest supported python version 
      os: '["windows-latest", "ubuntu-latest"]'
        # Description: Comma-separated list of operating systems to test against 
        # Default: ["ubuntu-latest"]
      package_manager_command: "pip install poetry"
        # Description: Command to install additional package manager 
        # Default: ""
      install_command: "poetry install --no-interaction"
        # Description: The command issued to install python packages 
        # Default: "pip install -r requirements.txt"
      test_command: "poetry run tox"
        # Description: The command used to run the test suite
        # Default: "pytest"
```

<a id="python_release"></a>

## Python Release 

Handles Python release automation, including version bumping and changelog generation. Runs on pushes to the default branch.

This repo is heavily reliant on the Release Please action which uses release types to set a sensible set of default files to interact with depending on the coding language used within the repo.

- [**Action release types**](https://github.com/googleapis/release-please-action#release-types-supported)

<br />

**Consumed actions**: 
- [**tibdex/github-app-token**](https://github.com/tibdex/github-app-token) 
- [**actions/checkout**](https://github.com/actions/checkout)
- [**googleapis/release-please-action**](https://github.com/googleapis/release-please-action)

<br />

**Example Options**

```yaml
with:
      release_type: "python"
        # Description: Built in release strategy
        # Default: "simple"
```

<a id="python_publish"></a>

## Python Publish

Publishes a Python package and runs on published releases.

**Consumed actions**: 
- [**tibdex/github-app-token**](https://github.com/tibdex/github-app-token) 
- [**actions/checkout**](https://github.com/actions/checkout)
- [**actions/setup-python**](https://github.com/actions/setup-python)

<br />

**Example Options**

```yaml
with:
      build_tooling_command: "pip install poetry"
        # Description: Command to install build tooling 
        # Default: "pip install build"
      build_command: "poetry build"
        # Description: The command used to build packages
        # Default: "python -m build"
```

<a id="todo_check"></a>

## TODO Check

Checks for unresolved TODOs in the codebase that are not linked to a ticket. Runs on PRs to the default branch and can be manually triggered.

**Consumed Actions**:
- [**actions/checkout**](https://github.com/actions/checkout)

```yaml
with:
      directory_to_scan: "./my_package"
        # Description: The root of the directory to scan
        # Default: "./"
      file_extensions: "py, json, yaml"
        # Description: A comma seperated list of file extensions to check
        # Default: "md"
```

<a id="file_check"></a>

## Python File Check

Ensures required files (README, CHANGELOG, etc.) are present and not empty. Runs on PRs to the default branch. There are no options here but it is only suitable for python based repos.

**Consumed actions**: 
- [**andstor/file-existence-action**](https://github.com/andstor/file-existence-action) 
- [**actions/checkout**](https://github.com/actions/checkout)

<a id="pr_title"></a>

## Conventional PR Title

Checks that pull request titles follow the Conventional Commits standard. Runs on PRs to the default branch. There are no options and this will work on all repos. This is important if you want to use the auto PR workflow. 

**Consumed actions**: 
- [**action-semantic-pull-request**](https://github.com/amannn/action-semantic-pull-request)

<a id="auto_pr"></a>

## Auto Pull Request

Automates the creation and management of pull requests, including branch name extraction and token generation. Runs on pushes (except to the default branch). There are no options and this should work on all repos but it is completely reliant on conventional commits. It also works best when each PR has a single CC which describes the aim of the PR.

**Consumed Actions**: 
- [**actions/checkout**](https://github.com/actions/checkout)
- [**tibdex/github-app-token**](https://github.com/tibdex/github-app-token)

## Python Test Gen

A reusable workflow for running tests with configurable Python versions and OS matrix. Intended to be called by other workflows.


**Consumed Actions**: 
- [actions/checkout](https://github.com/actions/checkout)

##

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[issues-shield]: https://img.shields.io/github/issues/renalreg/.github.svg?style=for-the-badge
[issues-url]: https://github.com/renalreg/.github/issues

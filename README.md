<a name="readme-top"></a>

<div align='center'>

[![Issues][issues-shield]][issues-url]

</div>
<br />
<h1 align="center">.github</h1>

## About The Project

A standard set of workflows and associated files that we should strive to reuse where possible.

## Usage
There are three main ways to incorporate the actions from this repository into another project:

* Using GitHub’s Actions Marketplace (for public repositories)
If your project is public, you can easily add these actions via the GitHub Actions tab. Navigate to the Actions tab in your repository, select New workflow, and search for actions published by the UK Kidney Association.

* Manual Copy (especially for private repositories)
For private repositories or custom setups, you can manually copy the workflow files into your project.
When doing this, make sure to copy the "caller" workflow, not the main workflow—unless you have a specific reason to modify the main workflow directly.

* Using Workflow Templates in .github Directory
Some workflow templates use the .github directory to manage reusable workflows. You can copy these templates into your project and fill out the required fields. This will enable your project to correctly invoke the workflows.

Why use the "caller" workflow?
By including only the caller in your repository, updates made to the main workflows in this central repo will automatically propagate to all consuming repositories. This design promotes maintainability and consistency across multiple projects. As a result, the workflows here are intentionally generic to support a wide range of use cases—but may require some customization for specific project needs.
## Conventional Commits

A lot of the workflows in this repo rely on the use of conventional commits. Check out the following documentation

- [**Conventional Commits**](https://www.conventionalcommits.org/en/v1.0.0/)
- [**Conventional Commits for VSCode**](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits)
  <br />

## Squash and Merge

If you have read the conventional commits documentation you will know that conventional commits go hand in hand with squash and merge. The workflows here also expect that to be the merging strategy. If you aren't yet in the know have a read

- [**Squash and Merge**](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#squash-and-merge-your-commits)

## Available Workflows

Below is a summary of the workflows provided in this repository:

## Conventional PR Title

Checks that pull request titles follow the Conventional Commits standard. Runs on PRs to the default branch.

- **caller path**: `.github/workflow-templates/conventional_pr_title_caller.yml`
- **consumed actions**: [action-semantic-pull-request](https://github.com/amannn/action-semantic-pull-request)

## Pull Request

Automates the creation and management of pull requests, including branch name extraction and token generation. Runs on pushes (except to the default branch) and can be manually triggered.

- **caller path**: `.github/workflow-templates/pull_request_caller.yml`
- **consumed actions**: [actions/checkout](https://github.com/actions/checkout), [tibdex/github-app-token](https://github.com/tibdex/github-app-token)

## Python File Check

Ensures required files (README, CHANGELOG, etc.) are present and not empty in a PR. Runs on PRs to the default branch.

- **caller path**: `.github/workflow-templates/python_file_check_caller.yml`
- **consumed actions**: [actions/checkout](https://github.com/actions/checkout), [andstor/file-existence-action](https://github.com/andstor/file-existence-action)

## Python Publish

Publishes a Python package on release and triggers tests. Runs on published releases and can be manually triggered.

- **caller path**: `.github/workflow-templates/python_publish_caller.yml`
- **consumed actions**: [tibdex/github-app-token](https://github.com/tibdex/github-app-token), [convictional/trigger-workflow-and-wait](https://github.com/convictional/trigger-workflow-and-wait), [actions/checkout](https://github.com/actions/checkout), [actions/setup-python](https://github.com/actions/setup-python), [Gr1N/setup-poetry](https://github.com/Gr1N/setup-poetry)

## Python Release

Handles Python release automation, including version bumping and changelog generation. Runs on pushes to the default branch and can be manually triggered.

- **caller path**: `.github/workflow-templates/python_release_caller.yml`
- **consumed actions**: [tibdex/github-app-token](https://github.com/tibdex/github-app-token), [actions/checkout](https://github.com/actions/checkout), [Gr1N/setup-poetry](https://github.com/Gr1N/setup-poetry), [google-github-actions/release-please-action](https://github.com/google-github-actions/release-please-action)

Handles Python release automation, including version bumping and changelog generation. Runs on pushes to the default branch and can be manually triggered.

## Python Test

Runs the Python test suite across multiple OSes and Python versions. Runs on PRs to the default branch and can be manually triggered.

- **caller path**: `.github/workflow-templates/python_test_caller.yml`
- **consumed actions**: [actions/checkout](https://github.com/actions/checkout), [Gr1N/setup-poetry](https://github.com/Gr1N/setup-poetry), [actions/setup-python](https://github.com/actions/setup-python)

## Python Test Gen

A reusable workflow for running tests with configurable Python versions and OS matrix. Intended to be called by other workflows.

- **caller path**: `.github/workflow-templates/python_test_gen_caller.yml`
- **consumed actions**: [actions/checkout](https://github.com/actions/checkout)

## TODO Check

Checks for unresolved TODOs in the codebase. Runs on PRs to the default branch and can be manually triggered.

- **caller path**: `.github/workflow-templates/todo_check_caller.yml`
- **consumed actions**: [actions/checkout](https://github.com/actions/checkout), [Gr1N/setup-poetry](https://github.com/Gr1N/setup-poetry), [actions/setup-python](https://github.com/actions/setup-python)

##

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[issues-shield]: https://img.shields.io/github/issues/renalreg/.github.svg?style=for-the-badge
[issues-url]: https://github.com/renalreg/.github/issues

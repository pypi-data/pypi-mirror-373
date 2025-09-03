# gh-actions-deliver-python-package

Custom GitHub Action to deliver a python package to a pypi repository (pypi.uoregon.edu).

Additionally, this README includes instructions to deploy to pypi.org or test.pypi.org via "pypa/gh-action-pypi-publish" GitHub Action.

> See also [gh-actions-test-python-package](https://is-github.uoregon.edu/Network-Services/gh-actions-test-python-package) which is used in the example(s) below.

## GitHub Self-Hosted Runner Requirements

- Python 3

## Your Project Requirements

Assuming you are using "pyproject.toml" to define your dependencies, all examples expect:

- Your "pyproject.toml" file contains "project.optional-dependencies"...
    - ... which includes the "cicd" array...
        - ... which contains AT LEAST `["build", "pytest", "pytest-cov"]`

Example of a satisfactory snippet in a "pyproject.toml" file:
```
[project.optional-dependencies]
cicd = [
  "build",
  "pytest",
  "pytest-cov",
]
```

## Example: Workflow for Publishing to pypi.uoregon.edu

1. Follow instructions to [Deploy to pypi.uoregon.edu (confluence)](https://confluence.uoregon.edu/x/ag5aGw).
    * NOTE: This example assumes you are using our default SSH Key pair found in keepass: "General -> PKI Keys -> pypi.uoregon.edu"
    * That default key pair is saved as [a Secret named `PYPI_UOREGON_EDU_SSH_KEY` in Network-Services GitHub Organization](https://is-github.uoregon.edu/organizations/Network-Services/settings/secrets/actions)
2. Save the workflow below as ".github/workflows/test-and-deliver.yml" to test and publish your python package at [pypi.uoregon.edu](https://pypi.uoregon.edu)
3. Recommended: Copy the ["Recommended Git Workflow" from the appendix below](#recommended-git-workflow) to your 'developer/contributor' documentation.

```yml
name: CICD

on:
  push:

jobs:
  automated-tests:
    runs-on:
      - python
      - self-hosted
    steps:
      -
        uses: actions/checkout@v4
      -
        name: Run automated tests
        uses: Network-Services/gh-actions-test-python-package@main
  deliver-to-pypi-uoregon-edu:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: automated-tests
    runs-on:
      - python
      - self-hosted
    steps:
      -
        uses: actions/checkout@v4
      -
        uses: Network-Services/gh-actions-deliver-python-package@main
        with:
          package-index: pypi.uoregon.edu
          pypi-ssh-key: ${{ secrets.PYPI_UOREGON_EDU_SSH_KEY }}
```

## Example: Workflow for Publishing to pypi.org

Deploying to pypi.org or test.pypi.org is done using "gh-action-pypi-publish" maintained by the Python Packaging Authority (PyPA).

> Why not integrated "gh-action-pypi-publish" into this Custom GitHub Action?
> Because, ["gh-action-pypi-publish" does not support being used within a Composite GitHub Action (such as this one)](https://github.com/pypa/gh-action-pypi-publish/issues/299).

1. Save the workflow below as ".github/workflows/test-and-deliver.yml"
2. Recommended: Copy the ["Recommended Git Workflow" from the appendix below](#recommended-git-workflow) to your 'developer/contributor' documentation.

> **ℹ Note:** PyPI Authorization Notes
> 
> - **pypi.org:** Recommend using [GitHub Secret `secrets.PYPI_API_TOKEN`](https://is-github.uoregon.edu/organizations/Network-Services/settings/secrets/actions/PYPI_API_TOKEN) to upload to pypi.org
>   - This is seen in the example below.
> - **test.pypi.org:** When publishing to test.pypi.org, use [GitHub Secret `secrets.TEST_PYPI_API_TOKEN`](https://is-github.uoregon.edu/organizations/Network-Services/settings/secrets/actions/TEST_PYPI_API_TOKEN).

```yml
name: CICD

on:
  push:

jobs:
  automated-tests:
    runs-on:
      - python
      - self-hosted
    steps:
      -
        uses: actions/checkout@v4
      -
        name: Run automated tests
        uses: Network-Services/gh-actions-test-python-package@main
  deliver-to-pypi-org:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: automated-tests
    runs-on:
      - python
      - self-hosted
    steps:
      -
        uses: actions/checkout@v4
      -
        name: Setup Python venv
        shell: bash
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install --upgrade pip build
      -
        name: Build package
        shell: bash
        run: |
          source .venv/bin/activate
          pyproject-build
      - 
        name: Publish distribution 📦 to PyPI
        uses: pypa/gh-action-pypi-publish@76f52bc884231f62b9a034ebfe128415bbaabdfc
        with:
          attestations: false
          password: ${{ secrets.PYPI_API_TOKEN }}
          # Want to publish to test.pypi.org instead? Use:
          # repository-url: https://test.pypi.org/legacy/
          # password: ${{ secrets.TEST_PYPI_API_TOKEN }}

```


# Appendix

## Recommended Git Workflow

When you are ready to release a new version of your python package, follow this Git Workflow:

- [ ] Update your version in your pyproject.toml
    - Follow [semantic versioning](https://semver.org/)
- [ ] Make a pull request into your `main` branch
    - This will trigger the "test" job 
- [ ] Merge the pull request into your `main` branch
    - This will trigger the "deliver" job (after running the "test" job)
- [ ] [Create a "Release"](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release) in this GitHub Repository.

## What is pypi.uoregon.edu?

Our Systems Automation Services team maintains a private Python Package Index (PyPI) service.

* Service URL https://pypi.uoregon.edu

> How to install packages from pypi.uoregon.edu:
> 
> * `pip install --extra-index-url https://pypi.uoregon.edu <your_package_name>`


# Development (for Maintainers of gh-actions-deliver-python-package)

Notes for future developers to maintain this solution.

## 'package-for-testing-gh-actions'

To test if this is a useful python package on this project, first set up a 'virtual environment' ('.venv):

```bash
python3 -m venv .venv && source .venv/bin/activate
```

Then install the package in editable mode

```
pip install -e .
```

## docs/github-cicd.md Snippet

We recommend following this README, and then copying the below contents into your project as the file "docs/github-cicd.md":

```
# GitHub Continuous Integration and Delivery

This project is delivered as the [<PACKAGE_NAME> package to pypi.uoregon.edu](https://pypi.uoregon.edu/<PACKAGE_NAME>/).

> Recommended Git Workflow below copied from [gh-actions-deliver-python-package](https://is-github.uoregon.edu/Network-Services/gh-actions-deliver-python-package?tab=readme-ov-file#recommended-git-workflow)

## Recommended Git Workflow

When you are ready to release a new version of your python package, follow this Git Workflow:

- [ ] Update your version in your pyproject.toml
    - Follow [semantic versioning](https://semver.org/)
- [ ] Make a pull request into your `main` branch
    - This will trigger the "test" job 
- [ ] Merge the pull request into your `main` branch
    - This will trigger the "deliver" job (after running the "test" job)
- [ ] [Create a "Release"](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release) in this GitHub Repository.

## test-and-deliver.yml

The "test-and-deliver.yml" GitHub Workflow is copied directly from [README of gh-actions-deliver-python-package](https://is-github.uoregon.edu/Network-Services/gh-actions-deliver-python-package?tab=readme-ov-file#example-workflow-for-publishing-to-pypiuoregonedu)
```

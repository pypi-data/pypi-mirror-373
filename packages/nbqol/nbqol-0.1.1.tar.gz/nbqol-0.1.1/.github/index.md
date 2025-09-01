# GitHub Workflows for NB-QOL

This repository contains the following GitHub workflows:

## Documentation Workflow

- **Path**: `.github/workflows/docs.yml`
- **Purpose**: Builds the Sphinx documentation and deploys it to the gh-pages branch for hosting on GitHub Pages.

## PyPI Publishing Workflow

- **Path**: `.github/workflows/publish.yml`
- **Purpose**: Publishes the package to PyPI when a new release is created or when manually triggered with a specific version.

## Build and Test Workflow

- **Path**: `.github/workflows/build-test.yml`
- **Purpose**: Builds the package and runs the test suite across multiple Python versions to ensure compatibility and functionality.

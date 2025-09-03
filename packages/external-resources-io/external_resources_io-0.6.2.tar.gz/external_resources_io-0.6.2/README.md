# External Resources IO

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![PyPI](https://img.shields.io/pypi/v/external-resources-io)][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
![PyPI - License](https://img.shields.io/pypi/l/external-resources-io)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

[pypi-link]:                https://pypi.org/project/external-resources-io/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/external-resources-io

Utility library to parse input data from App-Interface into External Resource modules.

## Development

This project targets Python version 3.11.x for best compatibility and leverages [uv](https://docs.astral.sh/uv/) for the dependency managment.

Create a local development environment with all required dependencies:

```sh
uv sync --python 3.11
```

## Testing

Run the test suite with [pytset](https://docs.pytest.org/en/stable/):

```sh
make test
```

## Releasing

Bump the version number in `pyproject.toml` and merge your PR. The release will be automatically published to PyPI via the Konflux CI/CD pipeline.

## End User CLI

This library provides a CLI to interact with the External Resources IO module. The CLI is automatically installed when you install the `cli` extra package:

```sh
uv add --group dev external-resources-io[cli]
```

You can now use the `external-resources-io` command to interact with the module.

```sh
external-resources-io --help
```

For example, generate a `variables.tf` Terraform HCL file based on your app-interface input model:

```sh
external-resources-io external-resources-io tf generate-variables-tf er_aws_elasticache.app_interface_input.AppInterfaceInput
```

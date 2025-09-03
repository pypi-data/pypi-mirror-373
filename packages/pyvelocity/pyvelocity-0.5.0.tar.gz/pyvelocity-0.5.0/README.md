# pyvelocity

[![Test](https://github.com/yukihiko-shinoda/pyvelocity/workflows/Test/badge.svg)](https://github.com/yukihiko-shinoda/pyvelocity/actions?query=workflow%3ATest)
[![CodeQL](https://github.com/yukihiko-shinoda/pyvelocity/workflows/CodeQL/badge.svg)](https://github.com/yukihiko-shinoda/pyvelocity/actions?query=workflow%3ACodeQL)
[![Code Coverage](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity/coverage.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity)
[![Maintainability](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity/maintainability.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity)
[![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/yukihiko-shinoda/pyvelocity)](https://codeclimate.com/github/yukihiko-shinoda/pyvelocity)
[![Python versions](https://img.shields.io/pypi/pyversions/pyvelocity.svg)](https://pypi.org/project/pyvelocity)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyukihiko-shinoda%2Fpyvelocity)](http://twitter.com/share?text=PyVelocity&url=https://pypi.org/project/pyvelocity/&hashtags=python)

Automates task to check configurations about Python project to follow best practices to increase development velocity.

## Attention

The development status of this package is Beta now. It may not be able to keep backward compatibility. Be careful to use, especially for CI.

## Available Checks

PyVelocity performs the following checks to ensure your Python project follows best practices:

### Core Configuration Checks

#### `line-length`

Ensures consistent line length settings across all Python development tools:

- **docformatter**: `wrap-descriptions` and `wrap-summaries`
- **isort**: `line_length`
- **Black**: `line-length`
- **flake8**: `max-line-length`
- **Ruff**: `line-length`
- **Pylint**: `format.max-line-length`

#### `using-py-project-toml`

Verifies that your project uses `pyproject.toml` for configuration instead of legacy files like `setup.cfg`.

### Project Metadata Checks

#### `classifiers`

Validates that Python version classifiers in `pyproject.toml` are consistent with the `requires-python` field. For example, if `requires-python = ">=3.9"`, the classifiers should include all supported Python versions from 3.9 to the latest available.

#### `requires-python`

Ensures that the `requires-python` field supports the latest stable Python version to encourage adoption of newer Python features and improvements.

#### `readme`

Checks that the `readme` field is properly configured as `"README.md"` in the `[project]` section of `pyproject.toml`.

### Package Configuration Checks

#### `zip-safe-false`

Verifies that `zip-safe = false` is set in the `[tool.setuptools]` section to prevent issues with modern Python packaging.

#### `typed`

Ensures proper type hint configuration for typed packages:

- Validates that `tool.setuptools.package-data` includes `"*" = ["py.typed"]`
- Checks for the presence of `py.typed` files in package directories

This check helps ensure your package properly declares itself as typed for better IDE support and type checking.

## Quickstart

### 1. Install

```console
pip install pyvelocity
```

### 2. Run command

Run the following command in your project directory (where `pyproject.toml` exists):

```console
pyvelocity
```

#### Expected Output

**Success**: If all checks pass, you'll see:

```console
Looks high velocity! ⚡️ 🚄 ✨
```

**Issues Found**: If checks fail, PyVelocity will display specific error messages and exit with a non-zero status code, making it perfect for CI/CD integration.

<!-- markdownlint-disable no-trailing-punctuation -->
## How do I...
<!-- markdownlint-enable no-trailing-punctuation -->

### Ignore specific check?

You can configure PyVelocity to ignore specific checks by adding them to the `filter` list in `pyproject.toml`. For example, to ignore the `line-length` and `typed` checks:

```toml
[tool.pyvelocity]
filter = [
  "line-length",
  "typed"
]
```

Available check IDs:

- `line-length`
- `using-py-project-toml` 
- `classifiers`
- `requires-python`
- `readme`
- `zip-safe-false`
- `typed`

## Credits

This package was created with [Cookiecutter] and the [yukihiko-shinoda/cookiecutter-pypackage] project template.

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[yukihiko-shinoda/cookiecutter-pypackage]: https://github.com/yukihiko-shinoda/cookiecutter-pypackage

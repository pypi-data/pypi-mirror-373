# Invoke Lint

[![Test](https://github.com/yukihiko-shinoda/invoke-lint/workflows/Test/badge.svg)](https://github.com/yukihiko-shinoda/invoke-lint/actions?query=workflow%3ATest)
[![CodeQL](https://github.com/yukihiko-shinoda/invoke-lint/workflows/CodeQL/badge.svg)](https://github.com/yukihiko-shinoda/invoke-lint/actions?query=workflow%3ACodeQL)
[![Test Coverage](https://api.codeclimate.com/v1/badges/935364d296051fb926c8/test_coverage)](https://codeclimate.com/github/yukihiko-shinoda/invoke-lint/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/935364d296051fb926c8/maintainability)](https://codeclimate.com/github/yukihiko-shinoda/invoke-lint/maintainability)
[![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/yukihiko-shinoda/invoke-lint)](https://codeclimate.com/github/yukihiko-shinoda/invoke-lint)
[![Dependabot](https://flat.badgen.net/github/dependabot/yukihiko-shinoda/invoke-lint?icon=dependabot)](https://github.com/yukihiko-shinoda/invoke-lint/security/dependabot)
[![Python versions](https://img.shields.io/pypi/pyversions/invokelint.svg)](https://pypi.org/project/invokelint)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyukihiko-shinoda%2Finvoke-lint)](http://twitter.com/share?text=Invoke%20Lint&url=https://pypi.org/project/invokelint/&hashtags=python)

Invokes Python dev tools at once.

## Attention

- The development status of this package is Beta now. It may not be able to keep backward compatibility. Be careful to use, especially for CI.
- Currently, each commands require to run in project home directory.

## Advantage

1. Covers major development tools and they are optional to install
1. Quick response for developer, slow but detail for CI
1. Available to place commands into your selected namespace

### 1. Covers major development tools and they are optional to install

You can choose which dev tool you'll install, this package doesn't force to install each of dev tools. It helps you to avoid conflicts or breaking your project's dependencies.

Supporting tools:

Linters:

- [Xenon]
- [Ruff]
- [Bandit]
- [dodgy]
- [Flake8]
- [pydocstyle] (Optional)
- [mypy]
- [Pylint]
- [Semgrep]

Formatters:

- [docformatter]
- [Ruff]
- [autoflake] (If you want to use it instead of Ruff)
- [isort] (If you want to use it instead of Ruff)
- [Black] (If you want to use it instead of Ruff)

For test and coverage:

- [pytest]
- [Coverage.py]

Package build:

- [build]

### 2. Quick response for developer, slow but detailed for CI

The commands for each kind of tasks are designed as unified into 2 main commands:

- For developer: Runs only quick responsive dev tools at once
- For CI (or final check): Runs slow but detailed responsive tools at once

### 3. Available to place commands into your selected namespace

This doesn't pollute your comfortable namespaces of command line tools. Thanks to [Invoke], you can place commands into your selected namespace. (See: [Quickstart](#quickstart))

## Representative commands

(Note that the namespaces of following commands can be changed as you like. See: [Quickstart](#quickstart))

### `inv style`

Formats code by following tools at once:

1. [docformatter]
2. [Ruff] format
3. [Ruff] check --fix

Optionally, you can use [autoflake], [isort], and [Black] instead of [Ruff] format by `inv style --no-ruff`:

1. [docformatter]
2. [autoflake]
3. [isort]
4. [Black]
5. [Ruff] check --fix

- `inv style --check` can only check.
- `inv style --ruff` can skip `ruff check --fix`.

### `inv lint`

Runs following fast linters at once:

1. [Xenon]
2. [Ruff]
3. [Bandit]
4. [dodgy]
5. [Flake8]
6. [pydocstyle] (Optional)

The format task ([described later](#inv-style)) also run before running above linters. You can skip them by `--skip-format` option.

### `inv lint.deep`

Runs following slow but detailed linters at once:

1. [mypy]
2. [Pylint]
3. [Semgrep]

### `inv radon`

Reports [radon] both code complexity and maintainability index.

### `inv test`

Runs fast tests (which is not marked `@pytest.mark.slow`) by [pytest].

See:

- [How to mark test functions with attributes — pytest documentation]
- [Working with custom markers — pytest documentation]

### `inv test.cov`

Runs all tests and report those coverage by [pytest] and [Coverage.py].

It also can dump the coverage as XML or HTML format.

### `inv dist`

Builds source and wheel packages into `dist/` directory by [build].  
(Currently, not support in Windows)

See:

- [Building and Distributing Packages with Setuptools - setuptools latest documentation]
- [Package Discovery and Namespace Packages - setuptools latest documentation]

## Quickstart

### 1. Install

We should use [uv] or one of the [dependency management tools] to resolve dependencies of many dev tools.

For example, in case when we use the [uv], then, `pyproject.toml` is like below:

```toml
[dependency-groups]
dev = [
    "autoflake",
    "bandit; python_version >= '3.7'",
    # If you want to use not Ruff but Black for formatting
    "black; python_version >= '3.7'",
    "build",
    "bump-my-version",
    "cohesion",
    # The coverage==3.5.3 is difficult to analyze its dependencies by dependencies management tool,
    # so we should avoid 3.5.3 or lower.
    # - Command: "pipenv install --skip-lock" fails 
    #   since it tries to parse legacy package metadata and raise InstallError
    #   · Issue #5595 · pypa/pipenv
    #   https://github.com/pypa/pipenv/issues/5595
    "coverage>=3.5.4",
    # The dlint less than 0.14.0 limits max version of flake8.
    # - dlint/requirements.txt at 0.13.0 · dlint-py/dlint
    #   https://github.com/dlint-py/dlint/blob/0.13.0/requirements.txt#L1
    "dlint>=0.14.0",
    # To the docformatter load pyproject.toml settings:
    "docformatter[tomli]; python_version < '3.11' and python_version >= '3.6'",
    "docformatter; python_version >= '3.11'",
    "dodgy",
    # The hacking depends flake8 ~=6.1.0 or ~=5.0.1 or ~=4.0.1.
    # We should avoid the versions that is not compatible with the hacking,
    # considering the speed of dependency calculation process
    "flake8!=6.0.0,!=5.0.0,>=4.0.1; python_version >= '3.6'",
    # To use flake8 --radon-show-closures
    "flake8-polyfill",
    # To use pyproject.toml for Flake8 configuration
    "Flake8-pyproject",
    # Latest hacking depends on legacy version of flake8, and legacy hacking doesn't narrow flake8 version.
    # When unpin hacking, it has possibility to install too legacy version of hacking.
    "hacking>=5.0.0; python_version >= '3.8'",
    "invokelint; python_version >= '3.7'",
    # If you want to use not Ruff but isort for formatting
    "isort",
    "mypy",
    # If you want to use
    "pydocstyle; python_version >= '3.6'",
    "pylint",
    "pytest",
    # Since the radon can't run when use pytest log format:
    # - Radon can't run when use pytest log fornat: `$()d` · Issue #251 · rubik/radon
    #   https://github.com/rubik/radon/issues/251
    "radon<6.0.0",
    "ruff; python_version >= '3.7'",
    "semgrep;python_version>='3.9' or python_version>='3.6' and platform_system=='Linux'",
    # To resolve type checking for `from invoke import Collection` in tasks.py
    "types-invoke",
    "xenon",
]
```

then:

```console
uv sync
source .venv/bin/activate
```

### 2. Implement

Create `tasks.py` in project directory:

```python
"""Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke
"""
from invoke import Collection

from invokelint import dist, lint, path, style, test

ns = Collection()
ns.add_collection(dist)
ns.add_collection(lint)
ns.add_collection(path)
ns.add_collection(style)
ns.add_collection(test)
```

Commands may be explicitly place with a different name than they were originally given via a name kwarg (or the 2nd regular arg):

```python
ns.add_collection(lint, 'namespace-you-wish')
```

See: [Constructing namespaces — Invoke documentation]

### 3. Check installation

```console
inv --list
```

### 4. Setup target package

This package reuses `setuptools` settings for package discovery for linting, formatting, and measuring coverage. You can check which package are discovered by `setuptools` and your project's settings, by following command:

```console
$ inv path
Setuptools detected packages: ['invokelint', 'invokelint.path']
Root packages: ['invokelint']
Setuptools detected Python modules: ['setup', 'tasks']
Existing test packages: ['tests']
Python file or directories to lint: ['invokelint', 'setup.py', 'tasks.py', 'tests']
Python file or directories to lint excluding test packages: ['invokelint', 'setup.py', 'tasks.py']
```

If result is not your expected, follow official documentation of `setuptools` to configure `pyproject.toml` (recommended), `setup.cfg`, or `setup.py`.

See: [Package Discovery and Namespace Packages - setuptools latest documentation]

<!-- markdownlint-disable no-trailing-punctuation -->
## How do I...
<!-- markdownlint-enable no-trailing-punctuation -->

### Suppress [`B101: assert_used`] in Bandit and [`assert (S101)`] in Ruff only in test files?

Set below configuration in `pyproject.toml`:

```toml
[tool.bandit.assert_used]
skips = ["tests/*"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]
```

Note that invoke-lint executes [Bandit] with option `--configfile=pyproject.toml`, so upper configuration will be applied.

See: [Configuration — Bandit documentation]

## Credits

This package was created with [Cookiecutter] and the [yukihiko-shinoda/cookiecutter-pypackage] project template.

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[yukihiko-shinoda/cookiecutter-pypackage]: https://github.com/audreyr/cookiecutter-pypackage
[Invoke]: https://pypi.org/project/invoke/
[dependency management tools]: https://packaging.python.org/en/latest/tutorials/managing-dependencies/
[uv]: https://pypi.org/project/uv/
[Ruff]: https://pypi.org/project/ruff/
[Bandit]: https://pypi.org/project/bandit/
[dodgy]: https://pypi.org/project/dodgy/
[Flake8]: https://pypi.org/project/flake8/
[pydocstyle]: https://pypi.org/project/pydocstyle/
[Xenon]: https://pypi.org/project/xenon/
[Pylint]: https://pypi.org/project/pylint/
[mypy]: https://pypi.org/project/mypy/
[Semgrep]: https://pypi.org/project/semgrep/
[radon]: https://pypi.org/project/radon/
[docformatter]: https://pypi.org/project/docformatter/
[isort]: https://pypi.org/project/isort/
[autoflake]: https://pypi.org/project/autoflake/
[Black]: https://pypi.org/project/black/
[pytest]: https://pypi.org/project/pytest/
[How to mark test functions with attributes — pytest documentation]: https://docs.pytest.org/en/latest/how-to/mark.html
[Working with custom markers — pytest documentation]: https://docs.pytest.org/en/latest/example/markers.html
[Coverage.py]: https://pypi.org/project/coverage/
[build]: https://pypi.org/project/build/
[Building and Distributing Packages with Setuptools - setuptools latest documentation]: https://setuptools.pypa.io/en/latest/setuptools.html
[Package Discovery and Namespace Packages - setuptools latest documentation]: https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
[Constructing namespaces — Invoke documentation]: https://docs.pyinvoke.org/en/latest/concepts/namespaces.html#nesting-collections
[`B101: assert_used`]: https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html
[`assert (S101)`]: https://docs.astral.sh/ruff/rules/assert/
[Configuration — Bandit documentation]: https://bandit.readthedocs.io/en/latest/config.html#scanning-behavior

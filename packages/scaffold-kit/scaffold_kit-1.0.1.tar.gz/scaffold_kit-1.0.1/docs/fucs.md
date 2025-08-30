---
title: FUCs
weight: 0
---

A collection of frequently used commands related to this project. I actually
need this.

## Bandit

Tool designed to find common security issues in Python code.

- Scan: `uv run bandit -r -c bandit.yaml .`

`bandit.yaml`:

```yaml
--8<-- "bandit.yaml"
```

Links:

- [Bandit](https://bandit.readthedocs.io/en/latest/index.html)

## MkDocs

Project documentation with Markdown.

- Serve (with `.env`): `uv run --env-file .env mkdocs serve`
- Build (with `.env`): `uv run --env-file .env mkdocs build`
- Deploy to Github Pages (with `.env`):
  `uv run --env-file .env mkdocs gh-deploy`

`mkdocs.yaml`:

```yaml
--8<-- "mkdocs.yaml"
```

!!! note "Kill running server on port 8888"

    1. Get PID (e.g. 14765): `$ lsof -n -i4TCP:8888`

    2. Kill PID: `$ kill -9 14765`

Links:

- [MkDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

## MyPy

Static type checker for Python.

- Check: `uv run mypy .`

!!! failure "Broken"

    TODO: Fix "There are no .py[i] files in…"

`mypy.ini`:

```ini
--8<-- "mypy.ini"
```

Links:

- [MyPy](https://mypy.readthedocs.io/en/stable/)

## Ruff

Python linter and code formatter.

- Lint (and fix): `uv run ruff check [--fix]`
- Format: `uv run ruff format`

`ruff.toml`:

```toml
--8<-- "ruff.toml"
```

Links:

- [Ruff](https://docs.astral.sh/ruff/)

## Sphinx

Generates documentation automatically from docstrings.

- Generate `.rst` stubs:
  `uv run sphinx-apidoc -o docs_sphinx src --force --module-first --no-toc`
- Build HTML: `uv run sphinx-build -b html docs_sphinx reference`

```rst
--8<-- "docs_sphinx/index.rst"
```

Links:

- [Sphinx](https://www.sphinx-doc.org/en/master/)

`docs_sphinx/index.rst`:

## UV

Python package and project manager.

- Add dependency: `uv add <package>`
- Add optional dependency: `uv add <package> --optional <name>`
- Remove optional dependency: `uv remove <package> --optional <name>`
- Update the project's environment: `uv sync`
- Include all optional dependencies: `uv sync --all-extras`
- Include optional dependency: `uv sync --extras <name>`

`pyproject.toml`:

```toml
--8<-- "pyproject.toml"
```

Links:

- [UV](https://docs.astral.sh/uv/)

## Yamllint

A linter for YAML files.

- Lint: `uv run yamllint --strict -c .yamllint.yaml .`

`.yamllint.yaml`:

```toml
--8<-- ".yamllint.yaml"
```

Links:

- [Yamllint](https://yamllint.readthedocs.io/en/stable/)

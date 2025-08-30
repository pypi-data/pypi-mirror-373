# Sphinx Documentation Setup

This guide shows how to scaffold and configure
[Sphinx](https://www.sphinx-doc.org/en/master/) for a Python codebase documented
with
[Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
It covers:

- Adding dependencies in `pyproject.toml`
- Running `sphinx-quickstart` for initial scaffolding
- Renaming the source directory
- Configuring `conf.py` with the correct path to `src`
- Creating `index.rst`
- Automating builds with [uv](https://docs.astral.sh/uv/)

1. Generate/regenerate `.rst` stubs in `sphinx_source`:
   `uv run sphinx-apidoc -o sphinx_source src --force --module-first --no-toc`
2. Build HTML into `reference`:
   `uv run sphinx-build -b html sphinx_source reference`

## 1. Add Documentation Dependencies

In your `pyproject.toml`, add a `docs` environment under
`[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
docs = [
  "sphinx~=8.2.3",
  "sphinx-favicon~=1.0.1",
  "myst-parser~=4.0.1",
]
```

Install the docs dependencies by running `uv sync --extra docs`.

This ensures you get [Sphinx](https://www.sphinx-doc.org/en/master/) and the
[sphinx-book-theme](https://github.com/executablebooks/sphinx-book-theme) theme
in a dedicated environment.

## 2. Scaffold Sphinx with Quickstart

From the project root run:

```bash
uv run sphinx-quickstart
```

When prompted:

- Separate source and build directories? **yes**
- Default source directory name? **sphinx_source**
- Default build directory name? **reference**

This creates:

```asc
backend/
├── reference/
├── sphinx_source/
│   ├── _static/
│   ├── _templates/
│   ├── conf.py
│   └── index.rst
├── Makefile
└── make.bat
```

## 3. Configure `conf.py`

Edit `sphinx-source/conf.py` to point at your code in `src/` and enable
[Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings):

```python
# pylint: disable=redefined-builtin
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

# Path to the project root: one level up from sphinx-source, then into src
HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(HERE, '../src'))

project = 'Scaffold Kit'
copyright = '2025, John Doe'
author = 'John Doe'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',      # Google-style docstrings
    'sphinx.ext.viewcode',
    'myst_parser',              # Markdown parser
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Markdown parser settings
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'sphinx_book_theme'    # (Optional) Custom theme
html_title = 'Scaffold Kit'      # (Optional) Overridden by `html_logo`
html_logo = '_static/logo.svg'      # (Optional) Place in `sphinx-source/_static/logo.svg`
# (Optional) Additional theme options
html_theme_options = {
    'repository_url': 'https://github.com/executablebooks/sphinx-book-theme',
    'use_repository_button': True,
}
```

## 4. Update `index.rst`

Update `sphinx-source/index.rst` to include your modules:

```rst
.. Backend documentation master file, created by
   sphinx-quickstart on Thu May 15 14:38:19 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Backend documentation
=====================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


.. toctree::
   :maxdepth: 4
   :caption: Contents:

   scaffold_kit

.. include:: ../SPHINX.md
   :parser: myst_parser.docutils_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

## 6. Automate with Hatch Script

Now you can generate and build your docs with:

```bash
uv run sphinx-build -b html sphinx_source build
```

This sequence:

1. Regenerates `.rst` stubs in `sphinx-source/`
2. Builds HTML into `docs/`

## 7. (Optional) Remove `Makefile`

Since [Hatch](https://hatch.pypa.io/latest/) handles the build, you can delete
or ignore `Makefile` and `make.bat`.

---

Your [Sphinx](https://www.sphinx-doc.org/en/master/) setup is now fully
automated, uses
[Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings),
and reflects your custom directory names. Feel free to extend with PDF output,
intersphinx mappings, or custom themes.

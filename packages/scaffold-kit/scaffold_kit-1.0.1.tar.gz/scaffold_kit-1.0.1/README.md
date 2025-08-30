# scaffold-kit

[![PyPI - Version](https://img.shields.io/pypi/v/scaffold-kit)](https://pypi.org/project/scaffold-kit/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/scaffold-kit)](https://pypi.org/project/scaffold-kit/)
[![GitHub License](https://img.shields.io/github/license/sidisinsane/scaffold-kit)](https://github.com/sidisinsane/scaffold-kit/blob/main/LICENSE)

A comprehensive toolkit for project initialization and structure management.
Create projects from structured data definitions, generate file checklists for
tracking progress, and visualize directory hierarchies with ASCII trees.

## Installation

Install from PyPI:

```bash
pip install scaffold-kit
```

Install with uv:

```bash
uv add scaffold-kit
```

Install development releases from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ scaffold-kit
```

Install development releases from TestPyPI with uv:

```bash
uv add --index https://test.pypi.org/simple/ --index https://pypi.org/simple/ scaffold-kit
```

## Usage

scaffold-kit provides four main commands for project management:

**Initialize a project with example files:**

```bash
scaffold-kit init [ignore-file|config-file|scaffold-file]
```

**Create project structure from YAML/JSON definition:**

```bash
scaffold-kit scaffold [--root]
```

**Generate a file checklist for progress tracking:**

```bash
scaffold-kit checklist
```

**Create an ASCII tree of directory structure:**

```bash
scaffold-kit tree [directory] [--ignore-file FILE]
```

## Links

- **[Repository][1]** - Main GitHub repository
- **[Package][2]** - PyPI package page
- **[Test Package][3]** - TestPyPI package page for development releases
- **[Getting Started][4]** - This README with basic usage and examples
- **[Full Documentation][5]** - Complete guides, tutorials, and examples
- **[API Reference][6]** - Detailed API documentation and code reference
- **[Issues & Bug Reports][7]** - Report bugs or request features

## Acknowledgments

- [uv][8] - Fast Python package installer and resolver
- [asdf][9] - Multi-language version manager
- [Semantic Release][10] - Automated versioning
- [Pre-commit][11] - Git hooks for code quality
- [MkDocs][12] - Documentation generator
- [Sphinx][13] - API documentation generator

[1]: https://github.com/sidisinsane/scaffold-kit
[2]: https://pypi.org/project/scaffold-kit/
[3]: https://test.pypi.org/project/scaffold-kit/
[4]: https://github.com/sidisinsane/scaffold-kit#readme
[5]: https://sidisinsane.github.io/scaffold-kit/
[6]: https://sidisinsane.github.io/scaffold-kit/reference/
[7]: https://github.com/sidisinsane/scaffold-kit/issues
[8]: https://docs.astral.sh/uv/
[9]: https://asdf-vm.com/
[10]: https://python-semantic-release.readthedocs.io/
[11]: https://pre-commit.com/
[12]: https://www.mkdocs.org/
[13]: https://www.sphinx-doc.org/

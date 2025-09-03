# cditools

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/nsls2/cditools/workflows/CI/badge.svg
[actions-link]:             https://github.com/nsls2/cditools/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/cditools
[conda-link]:               https://github.com/conda-forge/cditools-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/nsls2/cditools/discussions
[pypi-link]:                https://pypi.org/project/cditools/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/cditools
[pypi-version]:             https://img.shields.io/pypi/v/cditools
[rtd-badge]:                https://readthedocs.org/projects/cditools/badge/?version=latest
[rtd-link]:                 https://cditools.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->

## Pyright Configuration

The `pyrightconfig.json` file configures the
[Pyright type checker](https://github.com/microsoft/pyright) for this project.
It sets the type checking mode to "basic" for less strict analysis and disables
warnings about missing type stubs and untyped base classes. This helps minimize
unnecessary alerts from third-party libraries that lack type information,
allowing you to focus on type issues within your own codebase.

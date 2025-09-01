# BenchMatcha
[![build status][buildstatus-image]][buildstatus-url]

[buildstatus-image]: https://github.com/Spill-Tea/BenchMatcha/actions/workflows/python-app.yml/badge.svg?branch=main
[buildstatus-url]: https://github.com/Spill-Tea/BenchMatcha/actions?query=branch%3Amain

![logo](docs/source/_static/logo.svg)

BenchMatcha is your companion pytest-like runner to google benchmarks.
Analyze, plot, and save your results over time to evaluate regression
over the lifetime of a project.

<!-- omit in toc -->
## Table of Contents
- [BenchMatcha](#benchmatcha)
  - [Installation](#installation)
    - [Install from pypi](#install-from-pypi)
    - [Clone the repository](#clone-the-repository)
    - [Pip install directly from github.](#pip-install-directly-from-github)
  - [Development](#development)
  - [For Developers](#for-developers)
  - [License](#license)


## Installation
You have options.

### Install from pypi
```bash
pip install BenchMatcha
```

### Clone the repository
```bash
git clone https://github.com/Spill-Tea/BenchMatcha.git
cd BenchMatcha
pip install .
```

### Pip install directly from github.
```bash
pip install git+https://github.com/Spill-Tea/BenchMatcha@main
```

## Development

BenchMatcha is currently in the planning stages of development. This means the project
is not ready for production use, and may be prone to change api without much notice.


## For Developers
After cloning the repository, create a new virtual environment and run the following
commands:

```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

Running unit tests locally is straightforward with tox. Make sure
you have all python versions available required for your project
The `p` flag is not required, but it runs tox environments in parallel.
```bash
tox -p
```
Be sure to run tox before creating a pull request.

## License
[BSD-3](LICENSE)

# ![pyCFS](docs/source/_static/art/pyCFS_logo.svg)

[![PyPi Version](https://img.shields.io/pypi/v/pycfs.svg?style=flat-square)](https://pypi.org/project/pycfs/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pycfs.svg?style=flat-square)](https://pypi.org/project/pycfs/)
[![DOI](https://zenodo.org/badge/DOI/10.48550/arXiv.2405.03437.svg?style=flat-square)](https://doi.org/10.48550/arXiv.2405.03437)
[![GitLab stars](https://img.shields.io/gitlab/stars/opencfs/pycfs.svg?style=flat-square&logo=gitlab&label=Stars&logoColor=white)](https://gitlab.com/opencfs/pycfs)
[![Downloads](https://pepy.tech/badge/pycfs/month?style=flat-square)](https://pepy.tech/project/pycfs)

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/opencfs/pycfs?style=flat-square)](https://gitlab.com/opencfs/pycfs/-/pipelines)
[![coverage](https://gitlab.com/opencfs/pycfs/badges/main/coverage.svg)](https://gitlab.com/opencfs/pycfs/-/jobs)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Python library for automating and data handling tasks for openCFS. Available on [PyPI](https://pypi.org/project/pyCFS/).

For more information, please visit the [documentation page](https://opencfs.gitlab.io/pycfs/index.html).

### Included submodules:

- `pyCFS`: Automation library
- `pyCFS.application`: Library of application-focused python scripts.
- `pyCFS.data`: Data processing framework for CFS type hdf5 file format.
- `pyCFS.topt`: Topology Optimization with openCFS.

## Installation

PyCFS can be installed via pip. The recommended way is to use a virtual environment or conda environment. Install with

```bash
python -m pip install --upgrade pycfs
```

For more information see the [installation guide](https://opencfs.gitlab.io/pycfs/installation.html) in the documentation.

## Contributing

For a developer install see the [developer installation guide](https://opencfs.gitlab.io/pycfs/installation.html#developer-install). 
See the [contribution guidelines](https://opencfs.gitlab.io/pycfs/dev_source/dev_notes_main.html) in the documentation on how to contribute to the project.
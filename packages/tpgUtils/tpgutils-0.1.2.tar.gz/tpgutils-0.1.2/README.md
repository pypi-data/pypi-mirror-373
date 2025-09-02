# tpgUtils

[![image](https://img.shields.io/pypi/v/tpgUtils.svg)](https://python.org/pypi/tpgUtils)
[![image](https://img.shields.io/pypi/l/tpgUtils.svg)](https://python.org/pypi/tpgUtils)
[![image](https://img.shields.io/pypi/pyversions/tpgUtils.svg)](https://python.org/pypi/tpgUtils)

[![image](https://img.shields.io/pypi/dm/app_config?style=flat-square)](https://pypistats.org/packages/tpgUtils)
![Pipeline](https://gitlab.com/tpgllc/tpgUtils/badges/main/pipeline.svg)
![Coverage](https://gitlab.com/tpgllc/tpgUtils/badges/main/coverage.svg)

## Descripton

This package is currently being used to develop and test the gitlab pipeline

A collection of utilities commonly used in applications.  Currently

 - tpgPrint: Print reports to console, file or both



## Packaging Notes

### packaging requirements
build>=1.2.2
packaging>=24.2
twine>=6.0.1
wheel>=0.45.1


### packaging doc with setuptools

https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#package-discovery

  pip install --upgrade setuptools[core]

quick steps:
use src-layout
  pip install --upgrade build
  python -m build
  or
  uv build
  pip install --editable .

when done with dev
  pip uninstall <pkg-name>


### packaging doc
https://packaging.python.org/en/latest/tutorials/packaging-projects/
https://packaging.python.org/en/latest/overview/

oicd gitlab doc
https://stefan.sofa-rockers.org/2024/11/14/gitlab-trusted-publisher/?utm_source=chatgpt.com

### upload to pipy (test or prod)
  pip install --upgrade twine
 or
  uv sync --extra dev

#### upload to test env - scoped token
  py -m twine upload --repository testpypi/tpgUtils dist/*
https://test.pypi.org/project/example_package_YOUR_USERNAME_HERE.

#### upload to test env
  py -m twine upload --repository testpypi dist/*
or
  uv publish --publish-url https://test.pypi.org/legacy/ --token <your-token>

view package in test pypi
https://test.pypi.org/

### install package in local env:

  py -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-YOUR-USERNAME-HERE

### prod env

upload to prod env
  py -m twine upload --repository pypi dist/*
or
  uv publish --token <your-token>

view:
https://pypi.org/project/package-name




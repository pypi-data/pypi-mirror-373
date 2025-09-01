# Package Discovery

[![Test](https://github.com/yukihiko-shinoda/package-discovery/workflows/Test/badge.svg)](https://github.com/yukihiko-shinoda/package-discovery/actions?query=workflow%3ATest)
[![CodeQL](https://github.com/yukihiko-shinoda/package-discovery/workflows/CodeQL/badge.svg)](https://github.com/yukihiko-shinoda/package-discovery/actions?query=workflow%3ACodeQL)
[![Code Coverage](https://qlty.sh/gh/yukihiko-shinoda/projects/package-discovery/coverage.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/package-discovery)
[![Maintainability](https://qlty.sh/gh/yukihiko-shinoda/projects/package-discovery/maintainability.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/package-discovery)
[![Dependabot](https://flat.badgen.net/github/dependabot/yukihiko-shinoda/package-discovery?icon=dependabot)](https://github.com/yukihiko-shinoda/package-discovery/security/dependabot)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/packagediscovery)](https://pypi.org/project/packagediscovery)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyukihiko-shinoda%2Fpackage-discovery)](http://twitter.com/share?text=Package%20Discovery&url=https://pypi.org/project/packagediscovery/&hashtags=python)

Package discovery based on Setuptools.

## Advantage

1. Debug packages that Setuptools discovered
2. Easy to filter packages to root packages only

### 1. Debug packages that Setuptools discovered

You can check the discovered packages by running the following Python code.

print_packages.py:

```python
from packagediscovery import Setuptools

print(Setuptools().packages)
```

```bash
$ python print_packages.py
['packagediscovery']
```

Since Package Discovery settings of Setuptools is a bit complicated so that we may want to know what packages Setuptools are discovering now.

cf. [Package Discovery and Namespace Packages - setuptools documentation]

### 2. Easy to filter packages to root packages only

You can filter the discovered packages to only include root packages by using the `root_packages` property.

filter_packages.py:

```python
from packagediscovery import Packages, Setuptools

setuptools = Setuptools()
print(f"Packages = {setuptools.packages}")
print(f"Root packages = {Packages(setuptools.packages).list_roots_only}")
```

```bash
$ python filter_packages.py
Packages = ['pyvelocity', 'pyvelocity.checks', 'pyvelocity.configurations', 'pyvelocity.configurations.files', 'pyvelocity.configurations.files.sections', 'pyvelocity.configurations.files.sections.pylint', 'pyvelocity.configurations.tools', 'pyvelocity.configurations.files.sections.pylint', 'pyvelocity.configurations.files.sections', 'pyvelocity.configurations.files', 'pyvelocity.checks', 'pyvelocity.configurations.tools', 'pyvelocity.configurations']
Root packages = ['pyvelocity']
```

## Quickstart

Install the package

```bash
$ pip install packagediscovery
```

<!-- markdownlint-disable no-trailing-punctuation -->
## How do I...
<!-- markdownlint-enable no-trailing-punctuation -->

### Discover packages

```python
from packagediscovery import Setuptools

setuptools = Setuptools()
print(f"Packages = {setuptools.packages}")
```

### Discover py modules

```python
from packagediscovery import Setuptools

setuptools = Setuptools()
print(f"Py modules = {setuptools.py_modules}")
```

### Discover project root

```python
from packagediscovery import Setuptools

setuptools = Setuptools()
print(f"Project root = {setuptools.project_root}")
```

### Filter packages to root packages only

```python
from packagediscovery import Setuptools

setuptools = Setuptools()
print(f"Packages = {setuptools.packages}")
print(f"Root packages = {Packages(setuptools.packages).list_roots_only}")
```

## Credits

This package was created with [Cookiecutter] and the [yukihiko-shinoda/cookiecutter-pypackage] project template.

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[yukihiko-shinoda/cookiecutter-pypackage]: https://github.com/audreyr/cookiecutter-pypackage
[Package Discovery and Namespace Packages - setuptools documentation]: https://setuptools.pypa.io/en/latest/userguide/package_discovery.html

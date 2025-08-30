"""Call Setuptools API to list packages."""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

from setuptools.discovery import ConfigDiscovery
from setuptools.discovery import FlatLayoutModuleFinder
from setuptools.dist import Distribution


class Setuptools:
    """To access dist."""

    def __init__(self) -> None:
        distribution = Distribution()
        distribution.parse_config_files()
        self.config_discovery = ConfigDiscovery(distribution)
        self.config_discovery()

    @property
    def packages(self) -> list[str]:
        return cast("list[str]", self.config_discovery.dist.packages)

    def find_py_modules(self, modules_to_lint: list[str]) -> list[str]:
        if self.config_discovery.dist.py_modules:
            return cast("list[str]", self.config_discovery.dist.py_modules)
        exclude = [module for module in FlatLayoutModuleFinder.DEFAULT_EXCLUDE if module not in modules_to_lint]
        # sorted(): Since Windows returns different order from Linux.
        return sorted(FlatLayoutModuleFinder.find(self.project_root, exclude))

    @property
    def project_root(self) -> Path:
        return Path(self.config_discovery.dist.src_root or os.curdir).resolve()

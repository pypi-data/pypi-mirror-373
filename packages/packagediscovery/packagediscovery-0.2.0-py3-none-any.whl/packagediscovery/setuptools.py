"""Call Setuptools API to list packages."""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

from setuptools.discovery import ConfigDiscovery
from setuptools.discovery import FlatLayoutModuleFinder
from setuptools.dist import Distribution

__all__ = ["Setuptools"]


class Setuptools:
    """To access dist."""

    def __init__(self, *, modules_to_lint: list[str] | None = None) -> None:
        self.modules_to_lint = modules_to_lint or []
        distribution = Distribution()
        distribution.parse_config_files()
        config_discovery = ConfigDiscovery(distribution)
        config_discovery()
        self.dist = config_discovery.dist
        self._py_modules = self.dist.py_modules

    @property
    def packages(self) -> list[str]:
        return cast("list[str]", self.dist.packages)

    @property
    def py_modules(self) -> list[str]:
        if self._py_modules:
            return cast("list[str]", self._py_modules)
        self._py_modules = self._find_py_modules()
        return cast("list[str]", self._py_modules)  # pyright: ignore[reportUnnecessaryCast]

    def _find_py_modules(self) -> list[str]:
        exclude = [module for module in FlatLayoutModuleFinder.DEFAULT_EXCLUDE if module not in self.modules_to_lint]
        # sorted(): Since Windows returns different order from Linux.
        return sorted(FlatLayoutModuleFinder.find(self.project_root, exclude))

    @property
    def project_root(self) -> Path:
        return Path(self.dist.src_root or os.curdir).resolve()

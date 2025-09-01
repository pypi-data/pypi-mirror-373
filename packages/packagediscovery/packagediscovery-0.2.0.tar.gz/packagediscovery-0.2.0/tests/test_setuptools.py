"""Tests for setuptools module."""

from __future__ import annotations

from pathlib import Path

import pytest

from packagediscovery.setuptools import Setuptools


class TestSetuptools:
    """Tests for Setuptools."""

    def test_project_root(self) -> None:
        assert Setuptools().project_root == Path().absolute().resolve()

    @pytest.mark.parametrize(
        ("py_modules", "expected"),
        [
            (["test_module"], ["test_module"]),
            (None, []),
        ],
    )
    def test_py_modules(self, py_modules: list[str] | None, expected: list[str]) -> None:
        """The property: py_modules should be set appropriate py modules."""
        setuptools = Setuptools()
        # Reason: For testing pylint: disable=protected-access
        setuptools._py_modules = py_modules  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        assert setuptools.py_modules == expected

    def test_packages(self) -> None:
        assert Setuptools().packages, ["packagediscovery"]

    def test_modules_to_lint(self) -> None:
        """The property: py_modules should not be excluded the packages that is set by modules_to_lint."""
        modules_to_lint = [
            "setup",
            "conftest",
            "test",
            "tests",
            "example",
            "examples",
            # ---- Task runners ----
            "toxfile",
            "noxfile",
            "pavement",
            "dodo",
            "tasks",
            "fabfile",
            # ---- Other tools ----
            "conanfile",  # Connan: C/C++ build tool
            "manage",  # Django
        ]

        setuptools = Setuptools(modules_to_lint=modules_to_lint)
        # Reason: For testing pylint: disable=protected-access
        setuptools._py_modules = None  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        assert setuptools.py_modules == ["tasks"]

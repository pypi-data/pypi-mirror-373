"""Tests for filter_duplication."""

import pytest

from packagediscovery.packages import Packages
from packagediscovery.packages import PairPackage
from packagediscovery.packages import RootOnly


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (PairPackage("foo.bar", "foo"), True),
        (PairPackage("foo", "foo.bar"), False),
        (PairPackage("foo", "bar"), False),
    ],
)
def test_check_former_is_subpath(paths: PairPackage, *, expected: bool) -> None:
    """Function: former_is_subpath should return appropriate boolean."""
    assert paths.former_is_sub_package_of_later() == expected


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (PairPackage("foo.bar", "foo"), False),
        (PairPackage("foo", "foo.bar"), True),
        (PairPackage("foo", "bar"), False),
    ],
)
def test_check_later_is_subpath(paths: PairPackage, *, expected: bool) -> None:
    """Function: later_is_subpath should return appropriate boolean."""
    assert paths.later_is_sub_package_of_former() == expected


def test_update_list() -> None:
    modules = RootOnly()
    modules.list = ["pyvelocity.configurations"]
    modules.append_package_and_unset_any_sub_packages("pyvelocity")
    assert modules.list == ["pyvelocity"]


def test_filter_duplication() -> None:
    """Method: filter_duplication() should return only top package."""
    list_path = [
        "pyvelocity",
        "pyvelocity.checks",
        "pyvelocity.configurations",
        "pyvelocity.configurations.files",
        "pyvelocity.configurations.files.sections",
        "pyvelocity.configurations.files.sections.pylint",
        "pyvelocity.configurations.tools",
        "pyvelocity.configurations.files.sections.pylint",
        "pyvelocity.configurations.files.sections",
        "pyvelocity.configurations.files",
        "pyvelocity.checks",
        "pyvelocity.configurations.tools",
        "pyvelocity.configurations",
    ]
    assert Packages(list_path).list_roots_only == ["pyvelocity"]

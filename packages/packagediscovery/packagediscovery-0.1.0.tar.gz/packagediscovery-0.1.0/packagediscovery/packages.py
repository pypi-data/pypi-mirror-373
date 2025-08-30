"""Filter duplicated paths."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PairPackage:
    """Represents a pair of packages."""

    former: str
    later: str

    def former_is_sub_package_of_later(self) -> bool:
        return self.former.startswith(self.later)

    def later_is_sub_package_of_former(self) -> bool:
        return self.later.startswith(self.former)


@dataclass
class RootOnly:
    """Represents a collection of root-only packages."""

    def __init__(self) -> None:
        self.list: list[str] = []

    def append_package_and_unset_any_sub_packages(self, target_package: str) -> None:
        """Add path and remove any sub packages."""
        for package in self.list:
            paths = PairPackage(target_package, package)
            if paths.former_is_sub_package_of_later():
                return
            if paths.later_is_sub_package_of_former():
                self.list.remove(package)
                break
        self.list.append(target_package)

    @staticmethod
    def create(list_package: list[str]) -> RootOnly:
        """This function doesn't use comprehension for speed.

        The base of loop is not the list of argument but new list so the times of loop in the sub function is reduced.
        """
        filtered = RootOnly()
        for package in list_package:
            filtered.append_package_and_unset_any_sub_packages(package)
        return filtered


class Packages:
    """Represents a collection of packages."""

    def __init__(self, list_package: list[str]) -> None:
        self.list_package = list_package
        self.root_only: RootOnly | None = None

    @property
    def list_roots_only(self) -> list[str]:
        if not self.root_only:
            self.root_only = RootOnly.create(self.list_package)
        return self.root_only.list

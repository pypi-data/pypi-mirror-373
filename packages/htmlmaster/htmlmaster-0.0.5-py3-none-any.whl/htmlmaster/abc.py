"""
Contains the abstract class: HTMLMaker.

NOTE: this module is private. All functions and objects are available in the main
`htmlmaster` namespace - use that instead.

"""

from abc import ABC, abstractmethod

__all__ = []


class HTMLMaker(ABC):
    """Make an html object."""

    def __init__(self, rootcls: str = "main", style: str | None = None) -> None:
        self.__rootcls = rootcls
        self.__rootstyle = style

    def setrootcls(self, rootcls: str, /) -> None:
        """Set class name for the root node."""
        self.__rootcls = rootcls

    def getrootcls(self) -> str | None:
        """Get class name for the root node."""
        return self.__rootcls

    def setrootstyle(self, style: str | None, /) -> None:
        """Set default css style for the root node."""
        self.__rootstyle = style

    def getrootstyle(self, default: str = "") -> str:
        """Get default css style for the root node."""
        return default if self.__rootstyle is None else self.__rootstyle

    @abstractmethod
    def make(self) -> str:
        """Make a string representation of the html object."""

    def show(self) -> "HTMLRepr":
        """
        Show the html object.

        Returns
        -------
        HTMLRepr
            Represents an html object.

        """
        return HTMLRepr(self.make())

    def print(self) -> str:
        """
        Print the string representation of the html tree.

        Returns
        -------
        StrRepr
            Represents a string.

        """
        return StrRepr(self.make())


class HTMLRepr:
    """Represents an html object."""

    def __init__(self, html_str: str, /) -> None:
        self.__html_str = html_str

    def _repr_html_(self) -> str:
        return self.__html_str


class StrRepr:
    """Represents a string."""

    def __init__(self, html_str: str, /) -> None:
        self.__html_str = html_str

    def __repr__(self) -> str:
        return self.__html_str

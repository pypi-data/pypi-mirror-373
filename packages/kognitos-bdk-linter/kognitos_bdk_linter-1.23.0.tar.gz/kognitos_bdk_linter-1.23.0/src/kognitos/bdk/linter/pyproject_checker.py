import os
import tomllib
from typing import Union

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

from .book import BookChecker


class PyProjectChecker(BaseChecker):
    """
    PyProjectChecker checks the validity of entry points in pyproject.toml files for Kognitos books. It
    ensures that all entry point to a class decorated with book.
    """

    name = "kognitos-pyproject-checker"
    msgs = {
        "C7601": (  # message id
            # template of displayed message
            "Entry point %s in pyproject does not point to a class decorated with book",
            # message symbol
            "pyproject-bad-entry-point",
            # message description
            "All entrypoints for Kognitos books must point to a class decorated with book",
        ),
        "C7602": (  # message id
            # template of displayed message
            "Class %s defined in pyproject.toml cannot be found in the source code",
            # message symbol
            "pyproject-missing-class",
            # message description
            "The entry point class defined in pyproject.toml must exist in the source code",
        ),
        "C7603": (  # message id
            # template of displayed message
            "Module %s defined in pyproject.toml does not reference a valid module",
            # message symbol
            "pyproject-missing-module",
            # message description
            "The entry point module defined in pyproject.toml must correctly reference a valid Python module",
        ),
    }

    def __init__(self, linter: PyLinter) -> None:
        super().__init__(linter)
        self._pyproject_path = None
        self._classes = {}
        self._entry_points = {}
        self.root_node = None

    def open(self) -> None:
        self._pyproject_path = None
        self._classes = {}
        self._entry_points = {}

    def find_pyproject_toml(self, node: Union[nodes.ClassDef, nodes.Module]):
        """Finds the pyproject.toml file in the current directory or its parent directories."""
        file_path = node.root().file
        if not self._pyproject_path:
            self.root_node = node.root()

            if file_path:
                current_dir = os.path.dirname(file_path)

                # traverse up until the root or until finding pyproject.toml
                while current_dir and not os.path.exists(os.path.join(current_dir, "pyproject.toml")):
                    parent_dir = os.path.dirname(current_dir)
                    if parent_dir == current_dir:  # root reached
                        break
                    current_dir = parent_dir

                pyproject_path = os.path.join(current_dir, "pyproject.toml")
                if os.path.exists(pyproject_path):
                    self._pyproject_path = pyproject_path

    def get_entrypoints(self) -> dict:
        entry_points = {}
        if self._pyproject_path:
            with open(self._pyproject_path, "rb") as pyproject_file:
                pyproject_content = tomllib.load(pyproject_file)
                entry_points = pyproject_content.get("tool", {}).get("poetry", {}).get("plugins", {}).get("kognitos-book", {})

        return entry_points

    def close(self) -> None:
        entry_points = self.get_entrypoints()
        for key, value in entry_points.items():
            package_and_module, cls = value.split(":", maxsplit=1)
            qname = f"{package_and_module}.{cls}"

            if key not in self._entry_points:
                self.add_message("pyproject-missing-module", args=package_and_module, node=self.root_node)

            if key in self._entry_points and not self._entry_points[key]["is_valid"]:
                self.add_message(
                    "pyproject-missing-class",
                    args=cls,
                    node=self._entry_points[key]["node"],
                )

            if qname in self._classes:

                if not self._classes[qname]["is_book"]:  # the class is not a book
                    self.add_message(
                        "pyproject-bad-entry-point",
                        args=key,
                        node=self._classes[qname]["node"],
                    )

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        # find the actual path of the file
        self.find_pyproject_toml(node)
        file_path = node.root().file
        if file_path:
            names = []
            current = node
            while current:
                names.append(current.repr_name())
                current = current.parent
            qname = ".".join(reversed(names))

            self._classes[qname] = {"is_book": BookChecker.is_book(node), "node": node}

    def visit_module(self, node: nodes.Module):
        """Visit a module and check for the entry point class."""
        self.find_pyproject_toml(node)
        entry_points = self.get_entrypoints()
        for key, value in entry_points.items():
            expected_module, expected_class = value.split(":", maxsplit=1)
            if not expected_module or not expected_class:
                return

            if node.name == expected_module:
                found_class = any(isinstance(child, nodes.ClassDef) and child.name == expected_class for child in node.body)

                self._entry_points[key] = {"is_valid": found_class, "node": node}

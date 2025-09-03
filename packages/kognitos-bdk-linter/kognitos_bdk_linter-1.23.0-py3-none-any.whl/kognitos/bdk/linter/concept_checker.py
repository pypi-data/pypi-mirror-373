import os
import re
from pathlib import Path
from typing import List, Optional

import toml
from astroid import FunctionDef, Name, nodes
from pylint.checkers import BaseChecker

from kognitos.bdk.docstring import DocstringParseError, DocstringParser
from kognitos.bdk.klang.parser import KlangParser

from . import util


class ConceptChecker(BaseChecker):
    """
    ConceptChecker class checks if a class is a concept by looking for a specific decorator. It also
    checks if the concept has the required documentation block, and the necessary serialization methods.
    """

    name = "kognitos-concept-checker"
    msgs = {
        "C7901": (  # message id
            # template of displayed message
            "Concept %s is missing description",
            # message symbol
            "concept-missing-description",
            # message description
            "All concepts must have a description",
        ),
        "C7903": (  # message id
            # template of displayed message
            "Concept %s is missing documentation",
            # message symbol
            "concept-missing-documentation",
            # message description
            "All concepts must have a documentation block attached to them",
        ),
        "C7904": (  # message id
            # template of displayed message
            "Unable to parse documentation block for book %s",
            # message symbol
            "concept-bad-documentation",
            # message description
            "All concepts must have a correct documentation string attached to them",
        ),
        "C7905": (  # message id
            # template of displayed message
            "The concept %s is missing method from_bytes",
            # message symbol
            "concept-missing-from-bytes",
            # message description
            "All concepts must have a method called from_bytes that allows to serialize it",
        ),
        "C7906": (  # message id
            # template of displayed message
            "The concept %s is missing method to_bytes",
            # message symbol
            "concept-missing-to-bytes",
            # message description
            "All concepts must have a method called to_bytes that allows to deserialize it",
        ),
        "C7907": (  # message id
            # template of displayed message
            "The concept %s function from_bytes is not a classmethod",
            # message symbol
            "concept-from-bytes-not-class-method",
            # message description
            "The `from_bytes` function must be a classmethod.",
        ),
        "C7908": (  # message id
            # template of displayed message
            "The concept %s function to_bytes is not a method",
            # message symbol
            "concept-to-bytes-not-method",
            # message description
            "The `to_bytes` function must be a method.",
        ),
        "C7909": (  # message id
            # template of displayed message
            "The concept %s function from_bytes has a bad signature",
            # message symbol
            "concept-from-bytes-bad-signature",
            # message description
            "The `from_bytes` function must be a from_bytes(cls, data: bytes) -> Self.",
        ),
        "C7910": (  # message id
            # template of displayed message
            "The concept %s function to_bytes has a bad signature",
            # message symbol
            "concept-to-bytes-bad-signature",
            # message description
            "The `to_bytes` function must be a to_bytes(self) -> bytes.",
        ),
        "C7911": (  # message id
            # template of displayed message
            "The concept %s is missing is_a",
            # message symbol
            "concept-missing-is-a",
            # message description
            "All concepts must have an is_a value",
        ),
        "C7912": (  # message id
            # template of displayed message
            "Cannot parse name for concept %s. '%s' is not a valid noun phrase",
            # message symbol
            "concept-cannot-parse-english",
            # message description
            "All concepts must have a well formed noun phrase as their name",
        ),
        "C7913": (  # message id
            # template of displayed message
            "The concept %s is a partial dataclass or attrs. It inherits from %s that is not a dataclass or attrs",
            # message symbol
            "concept-invalid-class",
            # message description
            "All dataclass or attrs concepts must inherit from dataclasses or attrs and be a dataclass or attrs themselves. Make sure you're not missing a @dataclass or @define decorator",
        ),
        "C7914": (  # message id
            # template of displayed message
            "The concept %s is missing attribute %s in the docstring",
            # message symbol
            "concept-missing-attribute-docstring",
            # message description
            "All dataclass concepts must have all their attributes documented in the docstring",
        ),
        "C7915": (  # message id
            # template of displayed message
            "The concept '%s' has an invalid type '%s' on field '%s' on class '%s'",
            # message symbol
            "concept-invalid-type",
            # message description
            "All dataclass concepts must have valid types for their attributes",
        ),
        "C7916": (  # message id
            # template of displayed message
            "The concept '%s' cannot have an `unset` field assignment",
            # message symbol
            "concept-wrong-unset-field-usage",
            # message description
            "Opaque concepts are not allowed to define an `unset` value. It should be used on dataclasses and attrs concepts.",
        ),
        "C7917": (  # message id
            # template of displayed message
            "The concept '%s' is_a field '%s' does not follow the pattern '%s %s'",
            # message symbol
            "concept-missing-book-name-in-is-a",
            # message description
            "All concepts must follow the pattern '{book_name} {noun}' in their is_a field.",
        ),
    }

    @classmethod
    def is_concept(cls, node: nodes.ClassDef):
        return util.is_concept(node)

    @classmethod
    def concept_is_a(cls, node: nodes.ClassDef) -> List[str]:
        decorator = util.get_concept_decorator(node)

        if decorator:
            if hasattr(decorator, "args") and len(decorator.args) > 0:
                return next(decorator.args[0].infer()).value

            if hasattr(decorator, "keywords") and len(decorator.keywords) > 0:
                is_a_keyword = next(filter(lambda x: x.arg == "is_a", decorator.keywords), None)

                if is_a_keyword:
                    if isinstance(is_a_keyword.value, nodes.List):
                        return [next(arg.infer()).value for arg in is_a_keyword.value.elts]
                    return [next(is_a_keyword.value.infer()).value]

        return []

    def find_book_names_in_project(self, node: nodes.ClassDef) -> List[str]:
        """
        Read book names from pyproject.toml file by looking for the kognitos-book plugin section.
        Returns a list of book names found in the project.
        """
        file_path = node.root().file
        if not file_path:
            return []

        project_root = self._find_project_root(file_path)
        if not project_root:
            return []

        pyproject_path = os.path.join(project_root, "pyproject.toml")

        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                data = toml.load(f)

            book_plugins = data.get("tool", {}).get("poetry", {}).get("plugins", {}).get("kognitos-book", {})

            return list(book_plugins.keys())

        except (FileNotFoundError, toml.TomlDecodeError):
            return []

    def _find_project_root(self, file_path: str) -> Optional[str]:
        """
        Find the project root directory by looking for pyproject.toml.
        """

        try:
            current_path = Path(file_path).parent.resolve()

            for parent in [current_path] + list(current_path.parents):
                if (parent / "pyproject.toml").exists():
                    return str(parent)

        except (OSError, ValueError):
            pass

        return None

    @classmethod
    def validate_is_a_includes_book_name(cls, concept_is_a: List[str], book_name: str) -> List[str]:
        """
        Validate that at least one is_a value follows the pattern '{book_name} {noun}'.
        Returns a list of is_a values that don't follow the pattern.
        """
        if not book_name:
            return []

        escaped_book_name = re.escape(book_name.lower())
        pattern = rf"^{escaped_book_name}\s+\S+.*$"

        invalid_is_a_values = []
        for is_a_value in concept_is_a:
            if not re.match(pattern, is_a_value.lower()):
                invalid_is_a_values.append(is_a_value)

        return invalid_is_a_values

    @classmethod
    def extract_noun_from_is_a(cls, is_a_value: str, book_name: str) -> str:
        """
        Extract the noun part from an is_a value that follows the pattern '{book_name} {noun}'.
        Returns the noun part or the original value if the pattern doesn't match.
        """
        if not book_name or not is_a_value:
            return is_a_value

        is_a_lower = is_a_value.lower()
        book_name_lower = book_name.lower()

        if is_a_lower.startswith(book_name_lower):
            noun_part = is_a_value[len(book_name) :].strip()
            return noun_part if noun_part else is_a_value

        return is_a_value

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        if ConceptChecker.is_concept(node):
            concept_is_a = ConceptChecker.concept_is_a(node)
            if not concept_is_a:
                self.add_message("concept-missing-is-a", node=node, args=node.name)
                return

            for is_a in concept_is_a:
                try:
                    KlangParser.parse_noun_phrases(is_a)
                except SyntaxError:
                    self.add_message("concept-cannot-parse-english", node=node, args=(node.name, is_a))

            book_names = self.find_book_names_in_project(node)
            if book_names:
                for is_a in concept_is_a:
                    if not any(not ConceptChecker.validate_is_a_includes_book_name([is_a], book_name) for book_name in book_names):
                        noun = ConceptChecker.extract_noun_from_is_a(is_a, book_names[0])
                        self.add_message(
                            "concept-missing-book-name-in-is-a",
                            args=(node.repr_name(), is_a, book_names[0], noun),
                            node=node,
                        )

            # check that it has a doc block
            if not node.doc_node:
                self.add_message("concept-missing-documentation", args=node.repr_name(), node=node)
            else:

                docstring = node.doc_node.value
                try:
                    parser = DocstringParser()
                    parsed_docstring = parser.parse(docstring)

                    # check short description
                    if parsed_docstring.short_description:
                        short_description = parsed_docstring.short_description.strip()
                        if not short_description:
                            self.add_message(
                                "concept-missing-description",
                                args=node.repr_name(),
                                node=node.doc_node,
                            )
                    else:
                        self.add_message(
                            "concept-missing-description",
                            args=node.repr_name(),
                            node=node.doc_node,
                        )

                except DocstringParseError:
                    self.add_message(
                        "concept-bad-documentation",
                        args=node.repr_name(),
                        node=node.doc_node,
                    )

            is_from_bytes_present = False
            is_to_bytes_present = False

            if util.concept_unset_instance(node) and not util.is_dataclass_or_attrs(node):
                self.add_message("concept-wrong-unset-field-usage", args=(node.repr_name(),), node=node)

            if util.is_dataclass_or_attrs(node):
                fields = util.get_dataclass_field_names_recursive(node)

                # check all fields are documented in the @concept
                if node.doc_node:
                    try:
                        missing_attributes = util.get_missing_attributes_in_docstring(fields, node.doc_node.value)
                        for ma in missing_attributes:
                            self.add_message(
                                "concept-missing-attribute-docstring",
                                args=(node.repr_name(), ma),
                                node=node,
                            )
                    except DocstringParseError:
                        pass

                # check all fields have valid types
                nodes_with_invalid_types = util.get_invalid_type_nodes(node)
                for invalid_node in nodes_with_invalid_types:
                    concept_name = node.repr_name()
                    invalid_type_name = invalid_node.repr_name()

                    if not isinstance(invalid_node, (nodes.AnnAssign, nodes.Assign)):
                        assign_node = util.get_first_assign_parent(invalid_node)
                    else:
                        assign_node = invalid_node

                    if assign_node:
                        field_name, class_name = util.get_field_and_class_name(assign_node)
                    else:
                        # NOTE: We should never reach this code. We're just covering ourselves in
                        # case we find a scenario we're not accounting for.
                        field_name = "unknown"
                        class_name = "unknown"

                    self.add_message(
                        "concept-invalid-type",
                        args=(concept_name, invalid_type_name, field_name, class_name),
                        node=invalid_node,
                    )
            elif util.is_partial_dataclass_or_attrs(node):
                partial_classes = util.get_partial_dataclass_or_attrs(node)
                self.add_message(
                    "concept-invalid-class",
                    args=(node.repr_name(), ", ".join(partial_classes)),
                    node=node,
                )
            else:
                for child_node in node.body:
                    if isinstance(child_node, FunctionDef):
                        if child_node.name == "from_bytes":
                            is_from_bytes_present = True

                            if child_node.type != "classmethod":
                                self.add_message(
                                    "concept-from-bytes-not-class-method",
                                    args=node.repr_name(),
                                    node=child_node,
                                )

                            if (
                                not child_node.args
                                or not child_node.args.args
                                or len(child_node.args.args) != 2
                                or not child_node.args.annotations
                                or len(child_node.args.annotations) != 2
                                or not isinstance(child_node.args.annotations[1], Name)
                                or not child_node.args.annotations[1].name == "bytes"
                                or not child_node.returns
                                or not isinstance(child_node.returns, Name)
                                or not child_node.returns.name == "Self"
                            ):
                                self.add_message(
                                    "concept-from-bytes-bad-signature",
                                    args=node.repr_name(),
                                    node=child_node,
                                )

                            continue

                        if child_node.name == "to_bytes":
                            is_to_bytes_present = True

                            if child_node.type != "method":
                                self.add_message(
                                    "concept-to-bytes-not-method",
                                    args=node.repr_name(),
                                    node=child_node,
                                )

                            if (
                                not child_node.args.args
                                or len(child_node.args.args) != 1
                                or not child_node.args.annotations
                                or len(child_node.args.annotations) != 1
                                or not child_node.returns
                                or not isinstance(child_node.returns, Name)
                                or not child_node.returns.name == "bytes"
                            ):
                                self.add_message(
                                    "concept-to-bytes-bad-signature",
                                    args=node.repr_name(),
                                    node=child_node,
                                )

                            continue

                if not is_from_bytes_present:
                    self.add_message(
                        "concept-missing-from-bytes",
                        args=node.repr_name(),
                        node=node,
                    )

                if not is_to_bytes_present:
                    self.add_message(
                        "concept-missing-to-bytes",
                        args=node.repr_name(),
                        node=node,
                    )

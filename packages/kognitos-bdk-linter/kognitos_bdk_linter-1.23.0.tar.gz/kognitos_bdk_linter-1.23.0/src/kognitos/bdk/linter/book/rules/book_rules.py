from abc import ABC, abstractmethod

from astroid import ClassDef, InferenceError, NameInferenceError
from pylint.lint import PyLinter

from ... import util

# We will break this down into multiple files in the future, as we continue to add more rules.


class BookRule(ABC):
    @abstractmethod
    def check_rule(self, linter: PyLinter, node: ClassDef) -> None:
        pass


class TagsRule(BookRule):
    def check_rule(self, linter: PyLinter, node: ClassDef) -> None:
        decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.book_decorator.book")
        if not decorator:
            return

        if not hasattr(decorator, "keywords") or len(decorator.keywords) == 0:
            linter.add_message(
                "book-missing-tags",
                args=node.repr_name(),
                node=node,
            )
            return

        tags_keyword = next(filter(lambda x: x.arg == "tags", decorator.keywords), None)

        if not tags_keyword:
            linter.add_message(
                "book-missing-tags",
                args=node.repr_name(),
                node=node,
            )
            return

        try:
            tags_value = next(tags_keyword.value.infer())
            if not hasattr(tags_value, "elts") or not isinstance(tags_value.elts, list):
                linter.add_message(
                    "book-tags-not-list",
                    args=node.repr_name(),
                    node=tags_keyword.value,
                )
                return

        except (InferenceError, NameInferenceError):
            linter.add_message(
                "book-tags-not-list",
                args=node.repr_name(),
                node=tags_keyword.value,
            )
            return

        bad_naming_tags = []
        for tag_element in tags_value.elts:
            try:
                tag_value = next(tag_element.infer()).value
                if isinstance(tag_value, str) and (not tag_value or not tag_value[0].isupper()):  # Is empty or not capitalized
                    bad_naming_tags.append(tag_value)
            except (InferenceError, NameInferenceError):
                continue

        if bad_naming_tags:
            linter.add_message(
                "tags-bad-naming",
                args=(node.repr_name(), ", ".join(bad_naming_tags)),
                node=tags_keyword.value,
            )


class DiscoverRule(BookRule):
    def check_rule(self, linter: PyLinter, node: ClassDef) -> None:
        """
        Checks the coexistence and correctness of @discover, @invoke, and @discoverable functions
        in a book class. Ensures that:
        - If @discover exists, @invoke must also exist, and vice versa.
        - There is only one @discover and one @invoke function.
        - If both @discover and @invoke exist, there must be at least one @discoverable function.
        """
        # Use the correct decorator paths for discover, invoke, and discoverable functions
        discover_functions = util.get_functions_by_decorator_from_classdef(node, "kognitos.bdk.decorators.discover_decorator.discover")
        invoke_functions = util.get_functions_by_decorator_from_classdef(node, "kognitos.bdk.decorators.invoke_decorator.invoke")
        discoverable_functions = util.get_functions_by_decorator_from_classdef(node, "kognitos.bdk.decorators.discoverables_decorator.discoverables")

        # Check for missing @invoke when @discover exists
        if discover_functions and not invoke_functions:
            linter.add_message(
                "book-discover-missing-invoke",
                args=node.repr_name(),
                node=node,
            )
            return

        # Check for missing @discover when @invoke exists
        if invoke_functions and not discover_functions:
            linter.add_message(
                "book-invoke-missing-discover",
                args=node.repr_name(),
                node=node,
            )
            return

        # If both are present, ensure there's exactly one of each
        if discover_functions and invoke_functions:
            # Ensure that there is a @discoverable function
            if not discoverable_functions:
                linter.add_message(
                    "book-missing-discoverable-functions",
                    args=node.repr_name(),
                    node=node,
                )

            if len(discover_functions) > 1:
                linter.add_message(
                    "book-multiple-discover-functions",
                    args=node.repr_name(),
                    node=node,
                )
            if len(invoke_functions) > 1:
                linter.add_message(
                    "book-multiple-invoke-functions",
                    args=node.repr_name(),
                    node=node,
                )
            if discoverable_functions and len(discoverable_functions) > 1:
                linter.add_message(
                    "book-multiple-discoverable-functions",
                    args=node.repr_name(),
                    node=node,
                )

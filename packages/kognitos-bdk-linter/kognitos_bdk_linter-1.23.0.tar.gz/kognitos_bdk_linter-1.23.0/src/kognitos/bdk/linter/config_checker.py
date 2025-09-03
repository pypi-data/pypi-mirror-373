from astroid import nodes
from pylint.checkers import BaseChecker

from kognitos.bdk.docstring import DocstringParseError, DocstringParser

from . import util


class ConfigChecker(BaseChecker):
    """
    ConnectChecker

    This class is responsible for checking the documentation and type annotations of config properties.
    """

    name = "kognitos-config-checker"
    msgs = {
        "C7801": (  # message id
            # template of displayed message
            "Config %s is missing description",
            # message symbol
            "config-missing-description",
            # message description
            "All config properties must have a description",
        ),
        "C7803": (  # message id
            # template of displayed message
            "Config %s is missing documentation",
            # message symbol
            "config-missing-documentation",
            # message description
            "All config properties must have a documentation block attached to them",
        ),
        "C7804": (  # message id
            # template of displayed message
            "Unable to parse documentation block for function %s: %s",
            # message symbol
            "config-bad-documentation",
            # message description
            "All config properties must have a correct documentation string attached to them",
        ),
        "C7805": (  # message id
            # template of displayed message
            "Missing description for arg %s",
            # message symbol
            "config-missing-argument-description",
            # message description
            "All arguments must have a description",
        ),
        "C7806": (  # message id
            # template of displayed message
            "Missing property for config %s",
            # message symbol
            "config-missing-property",
            # message description
            "All config properties must be properties decorated with @property",
        ),
        "C7807": (  # message id
            # template of displayed message
            "Unsupported type for return %s",
            # message symbol
            "config-return-unsupported-type",
            # message description
            "BCI supports a limited set of types",
        ),
        "C7808": (  # message id
            # template of displayed message
            "Unable to infer type for return %s",
            # message symbol
            "config-return-cannot-infer-type",
            # message description
            "Internal Error. Unable to infer the type for the return type.",
        ),
        "C7809": (  # message id
            # template of displayed message
            "Missing type annotation for %s",
            # message symbol
            "config-return-missing-type-annotation",
            # message description
            "All @config properties must have a return type annotation",
        ),
        "C7810": (  # message id
            # template of displayed message
            "Invalid name for config %s",
            # message symbol
            "config-invalid-name",
            # message description
            "No config configuration can be named 'connect'",
        ),
    }

    @classmethod
    def is_config(cls, node: nodes.FunctionDef):
        return bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.config_decorator.config"))

    @classmethod
    def is_property(cls, node: nodes.FunctionDef):
        return bool(util.get_decorator_by_name(node, "builtins.property"))

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        if ConfigChecker.is_config(node):
            # check that it has a doc block
            if not node.doc_node:
                self.add_message("config-missing-documentation", node=node)
                return

            docstring = node.doc_node.value
            try:
                parser = DocstringParser()
                parsed_docstring = parser.parse(docstring)

                # check short description
                if parsed_docstring.short_description:
                    short_description = parsed_docstring.short_description.strip()
                    if not short_description:
                        self.add_message(
                            "config-missing-description",
                            args=node.repr_name(),
                            node=node.doc_node,
                        )
                else:
                    self.add_message(
                        "config-missing-description",
                        args=node.repr_name(),
                        node=node.doc_node,
                    )

            except DocstringParseError as ex:
                self.add_message(
                    "config-bad-documentation",
                    args=[node.repr_name(), str(ex)],
                    node=node.doc_node,
                )

            if not ConfigChecker.is_property(node):
                self.add_message(
                    "config-missing-property",
                    args=node.repr_name(),
                    node=node,
                )

            if node.returns:
                invalid_return_nodes = util.get_invalid_type_nodes(node.returns)
                if any(invalid_return_nodes):
                    self.add_message(
                        "config-return-unsupported-type",
                        args=node.returns.repr_name(),
                        node=node.returns,
                    )
            else:
                self.add_message(
                    "config-return-missing-type-annotation",
                    args=node.repr_name(),
                    node=node,
                )

            def is_named_connection(node: nodes.FunctionDef) -> bool:
                config_decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.config_decorator.config")

                if hasattr(config_decorator, "keywords") and any(k.arg == "name" and k.value.value == "connection" for k in config_decorator.keywords):  # type: ignore [reportOptionalMemberAccess]
                    return True

                if hasattr(config_decorator, "args") and len(config_decorator.args) >= 1 and config_decorator.args[0].value == "connection":  # type: ignore [reportOptionalMemberAccess]
                    return True

                if node.name == "connection":
                    return True

                return False

            if is_named_connection(node):
                self.add_message(
                    "config-invalid-name",
                    args=node.repr_name(),
                    node=node,
                )

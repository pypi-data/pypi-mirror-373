from urllib.parse import urlparse

import astroid
from astroid import Instance, nodes
from pylint.checkers import BaseChecker

from kognitos.bdk.decorators import OAuthFlow, OAuthProvider

from . import util


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class OAuthChecker(BaseChecker):

    name = "kognitos-oauth-checker"
    msgs = {
        "C7701": (  # message id
            # template of displayed message
            "%s is not a valid URL",
            # message symbol
            "oauth-bad-authorize-endpoint",
            # message description
            "The authorize endpoint must be a valid URL",
        ),
        "C7702": (  # message id
            # template of displayed message
            "%s is not a valid URL",
            # message symbol
            "oauth-bad-token-endpoint",
            # message description
            "The token endpoint must be a valid URL",
        ),
        "C7703": (  # message id
            # template of displayed message
            "%s is not a valid OAuth provider",
            # message symbol
            "oauth-bad-provider",
            # message description
            f"The OAuth provider must be one of the following {', '.join(member.name for member in OAuthProvider)}",
        ),
        "C7704": (  # message id
            # template of displayed message
            "Flows must be a list",
            # message symbol
            "oauth-bad-flows-not-list",
            # message description
            "The supported OAuth flows must be a list",
        ),
        "C7705": (  # message id
            # template of displayed message
            "%s is not a valid OAuth flow",
            # message symbol
            "oauth-bad-flows-not-valid-flow",
            # message description
            f"The OAuth flow must be one of the following {', '.join(member.name for member in OAuthFlow)}",
        ),
        "C7706": (  # message id
            # template of displayed message
            "Scopes must be a list",
            # message symbol
            "oauth-bad-scopes-not-list",
            # message description
            "The OAuth scopes required must be provided as a list of strings",
        ),
    }

    @classmethod
    def oauth_decorator(cls, node: nodes.ClassDef):
        return util.get_decorator_by_name(node, "kognitos.bdk.decorators.oauth_decorator.oauth")

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        decorator = OAuthChecker.oauth_decorator(node)
        if decorator:
            for keyword in decorator.keywords:
                if keyword.arg == "authorize_endpoint":
                    value = next(keyword.value.infer()).value
                    if not is_valid_url(value):
                        self.add_message(
                            "oauth-bad-authorize-endpoint",
                            args=value,
                            node=keyword,
                        )
                elif keyword.arg == "token_endpoint":
                    value = next(keyword.value.infer()).value
                    if not is_valid_url(value):
                        self.add_message(
                            "oauth-bad-token-endpoint",
                            args=value,
                            node=keyword,
                        )
                elif keyword.arg == "provider":
                    inferred = next(keyword.value.infer())
                    value = (
                        inferred.parent.value.value
                        if (isinstance(inferred, Instance) and ("enum.Enum" in [ancestor.qname() for ancestor in inferred.ancestors()]))
                        else inferred.value
                    )
                    try:
                        OAuthProvider(value)
                    except ValueError:
                        self.add_message(
                            "oauth-bad-provider",
                            args=value,
                            node=keyword,
                        )
                elif keyword.arg == "flows":
                    inferred = next(keyword.value.infer())
                    if not inferred.qname() == "builtins.NoneType":
                        if not isinstance(inferred, astroid.List):
                            self.add_message(
                                "oauth-bad-flows-not-list",
                                args=None,
                                node=keyword,
                            )
                        else:
                            for elt in inferred.elts:
                                elt_inferred = next(elt.infer())
                                value = (
                                    elt_inferred.parent.value.value
                                    if (isinstance(elt_inferred, Instance) and ("enum.Enum" in [ancestor.qname() for ancestor in elt_inferred.ancestors()]))
                                    else elt_inferred.value
                                )
                                try:
                                    OAuthFlow(value)
                                except ValueError:
                                    self.add_message(
                                        "oauth-bad-flows-not-valid-flow",
                                        args=value,
                                        node=keyword,
                                    )
                elif keyword.arg == "scopes":
                    inferred = next(keyword.value.infer())
                    if not inferred.qname() == "builtins.NoneType":
                        if not isinstance(inferred, astroid.List):
                            self.add_message(
                                "oauth-bad-scopes-not-list",
                                args=None,
                                node=keyword,
                            )

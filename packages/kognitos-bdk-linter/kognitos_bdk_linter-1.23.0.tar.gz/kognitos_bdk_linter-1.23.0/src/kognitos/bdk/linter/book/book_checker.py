import os
from typing import Set, Tuple

import astroid
import uritemplate
from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

from kognitos.bdk.api import NounPhrase
from kognitos.bdk.docstring import DocstringParseError, DocstringParser
from kognitos.bdk.klang.parser import KlangParser
from kognitos.bdk.reflection import (BookProcedureDescriptor, ConceptAnyType,
                                     ConceptDescriptor, ConceptDictionaryType,
                                     ConceptListType, ConceptOpaqueType,
                                     ConceptOptionalType, ConceptScalarType,
                                     ConceptType, ConceptUnionType)

from .. import util
from .book_rule_factory import BookRuleFactory, DefaultBookRuleFactory


def is_english_match(blueprint_procedure: BookProcedureDescriptor, book_procedure: BookProcedureDescriptor):
    """
    Check if the blueprint procedure and book procedure are an english match.
    """

    def _target_matches():
        if blueprint_procedure.english_signature.target:
            return blueprint_procedure.english_signature.target == book_procedure.english_signature.target
        return True

    def _preposition_matches():
        if blueprint_procedure.english_signature.preposition:
            return blueprint_procedure.english_signature.preposition == book_procedure.english_signature.preposition
        return True

    verbs_match = blueprint_procedure.english_signature.verbs == book_procedure.english_signature.verbs
    object_matches = blueprint_procedure.english_signature.object == book_procedure.english_signature.object
    target_matches = _target_matches()
    preposition_matches = _preposition_matches()

    return all((verbs_match, preposition_matches, object_matches, target_matches))


def is_equivalent_is_a(blueprint_is_a: Set[NounPhrase], book_is_a: Set[NounPhrase]):
    """
    Check if the blueprint `is_a` field is a subset of the book `is_a` field.

    Example:
        1)
            blueprint_is_a = {"car"}
            book_is_a = {"car", "vehicle"}

            is_equivalent_is_a(blueprint_is_a, book_is_a) -> True


        2)
            blueprint_is_a = {"car"}
            book_is_a = {"cool car"}

            is_equivalent_is_a(blueprint_is_a, book_is_a) -> True
    """

    def compare_noun_phrase(bp_np: NounPhrase, bk_np: NounPhrase):
        head_match = bp_np.head == bk_np.head

        if bp_np.modifiers and bk_np.modifiers and len(bp_np.modifiers) <= len(bk_np.modifiers):
            return head_match and bp_np.modifiers == bk_np.modifiers[-len(bp_np.modifiers) :]

        if bp_np.modifiers == bk_np.modifiers or not bp_np.modifiers:
            return head_match

        return False

    return all(any(compare_noun_phrase(bp_np, bk_np) for bk_np in book_is_a) for bp_np in blueprint_is_a)


def is_equivalent_concept_type(bp_type: ConceptType, bk_type: ConceptType):
    """
    Check if two concept types are equivalent. For base types, we check for equality.
    For complex types, we check for equivalence. For example, any @concept either opaque or dictionary type,
    we check that the blueprint concept `is_a` field is a subset of the book concept `is_a` field.
    """
    if isinstance(bp_type, (ConceptScalarType)):
        return bp_type == bk_type

    if isinstance(bp_type, ConceptListType):
        return isinstance(bk_type, ConceptListType) and is_equivalent_concept_type(bp_type.type, bk_type.type)

    if isinstance(bp_type, ConceptOptionalType):
        return isinstance(bk_type, ConceptOptionalType) and is_equivalent_concept_type(bp_type.type, bk_type.type)

    if isinstance(bp_type, ConceptUnionType):
        return (
            isinstance(bk_type, ConceptUnionType)
            and len(bp_type.inners) == len(bk_type.inners)
            and all(is_equivalent_concept_type(bpt, bkt) for bpt, bkt in zip(bp_type.inners, bk_type.inners))
        )

    if isinstance(bp_type, ConceptAnyType):
        return True

    if isinstance(bp_type, (ConceptDictionaryType, ConceptOpaqueType)):
        return isinstance(bk_type, (ConceptDictionaryType, ConceptOpaqueType)) and is_equivalent_is_a(bp_type.is_a, bk_type.is_a)

    if isinstance(bp_type, type[None]) and isinstance(bk_type, type[None]):  # type: ignore [reportArgumentType]
        return True

    return False


def match_input_concept_to_procedure_node(concept_descriptor: ConceptDescriptor, book_procedure: Tuple[nodes.FunctionDef, BookProcedureDescriptor]):
    """
    Given an input concept descriptor, find the corresponding argument node in the book procedure FunctionDef.
    """
    book_procedure_node, book_procedure_descriptor = book_procedure
    parameter_concept_bind = next(filter(lambda p: concept_descriptor.noun_phrases in [c.noun_phrases for c in p.concepts], book_procedure_descriptor.parameter_concept_map))
    return next(filter(lambda arg: arg.name == parameter_concept_bind.python_name, book_procedure_node.args.arguments))


def extract_unmatched_inputs(book_procedure_descriptor: BookProcedureDescriptor, matched_inputs: list[ConceptDescriptor]):
    """
    Given a set of matched inputs and a book procedure descriptor, extract the unmatched inputs.

    The criteria for an unmatched input is one that is:

    1) Not in the matched inputs
    2) A mandatory input
    3) Not the target
    """

    def is_valid_input(input_concept: ConceptDescriptor):
        if input_concept in matched_inputs:
            return True

        if isinstance(input_concept.type, ConceptOptionalType):
            return True

        if input_concept.noun_phrases == book_procedure_descriptor.english_signature.target:
            return True

        return False

    book_input_concepts = book_procedure_descriptor.input_concepts or []

    return [x for x in book_input_concepts if not is_valid_input(x)]


def check_blueprint_procedure_and_book_procedure_inputs_and_outputs(
    checker, blueprint_procedure: BookProcedureDescriptor, book_procedure: Tuple[nodes.FunctionDef, BookProcedureDescriptor]
):
    """
    Check that the inputs and outputs match between the blueprint procedure and book procedure.
    """
    book_procedure_node, book_procedure_descriptor = book_procedure
    matched_inputs = []
    bp_input_concepts = blueprint_procedure.input_concepts or []
    book_input_concepts = book_procedure_descriptor.input_concepts or []

    # Check inputs
    for bp_input_concept in bp_input_concepts:
        matching = next((x for x in book_input_concepts if bp_input_concept.noun_phrases == x.noun_phrases), None)

        if not matching:
            checker.add_message("book-missing-blueprint-procedure-input-concept", args=(util.noun_phrases_to_string(bp_input_concept.noun_phrases)), node=book_procedure_node)
            continue

        matched_inputs.append(matching)

        if not is_equivalent_concept_type(bp_input_concept.type, matching.type):
            matching_node = match_input_concept_to_procedure_node(bp_input_concept, book_procedure)
            checker.add_message("book-wrong-blueprint-procedure-input-concept-type", args=(util.noun_phrases_to_string(bp_input_concept.noun_phrases)), node=matching_node)

    unmatched_inputs = extract_unmatched_inputs(book_procedure_descriptor, matched_inputs)

    for unmatched_input in unmatched_inputs:
        matching_node = match_input_concept_to_procedure_node(unmatched_input, book_procedure)
        checker.add_message("book-unexpected-blueprint-procedure-input-concept", args=(util.noun_phrases_to_string(unmatched_input.noun_phrases)), node=matching_node)

    matched_outputs = []

    bp_output_concepts = blueprint_procedure.output_concepts or []
    book_output_concepts = book_procedure_descriptor.output_concepts or []

    # Check outputs
    for bp_output_concept in bp_output_concepts:
        matching = next((x for x in book_output_concepts if bp_output_concept.noun_phrases == x.noun_phrases), None)

        if not matching:
            checker.add_message("book-missing-blueprint-procedure-output-concept", args=(util.noun_phrases_to_string(bp_output_concept.noun_phrases)), node=book_procedure_node)
            continue

        matched_outputs.append(matching)

        if not is_equivalent_concept_type(bp_output_concept.type, matching.type):
            checker.add_message(
                "book-wrong-blueprint-procedure-output-concept-type", args=(util.noun_phrases_to_string(bp_output_concept.noun_phrases)), node=book_procedure_node.returns
            )


def find_blueprint_match(blueprint_procedure: BookProcedureDescriptor, book_procedures: list[Tuple[nodes.FunctionDef, BookProcedureDescriptor]]):
    """
    Find the matching procedure from the blueprint in the book. This check is only an english check.
    """
    return next(filter(lambda x: is_english_match(blueprint_procedure, x[1]), book_procedures), None)


def format_procedure_code_for_error_message(procedure: nodes.FunctionDef):
    code_snippet = "\n".join(procedure.as_string().splitlines())
    code_snippet = code_snippet.replace("@blueprint_procedure", "@procedure")
    return "\n\n" + code_snippet + "\n\n"


def check_blueprint(checker, book: astroid.ClassDef, blueprint: astroid.ClassDef, book_procedures: list[nodes.FunctionDef]):
    blueprint_procedures = BookChecker.blueprint_procedures_from_classdef(blueprint)

    for blueprint_procedure in blueprint_procedures:
        try:
            blueprint_procedure_descriptor = util.create_blueprint_procedure_descriptor(blueprint_procedure)
            book_procedures_descriptors = [(book_procedure, util.create_procedure_descriptor(book_procedure)) for book_procedure in book_procedures]
            matched_procedure_descriptor = find_blueprint_match(blueprint_procedure_descriptor, book_procedures_descriptors)

            if not matched_procedure_descriptor:
                checker.add_message(
                    "book-missing-blueprint-procedure-implementation", args=(book.repr_name(), format_procedure_code_for_error_message(blueprint_procedure)), node=book
                )
                continue

            check_blueprint_procedure_and_book_procedure_inputs_and_outputs(checker, blueprint_procedure_descriptor, matched_procedure_descriptor)
        except ValueError:
            # Note : By passing procedure having missing docstring (It will crash as function
            # node doesn't have doc_node). Missing docstring will be captured in procedure checker
            pass


def check_blueprints(checker, node: astroid.ClassDef):
    blueprints = BookChecker.book_blueprints(node)
    book_procedures = BookChecker.procedures_from_classdef(node)

    for blueprint in blueprints:
        blueprint_classdef: nodes.ClassDef = next(blueprint.infer())  # type: ignore
        check_blueprint(checker, node, blueprint_classdef, book_procedures)


def check_oauth_params_in_docstring(checker: BaseChecker, node: astroid.ClassDef, parsed_docstring):
    oauth_decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.oauth_decorator.oauth")
    if not oauth_decorator:
        return

    authorize_endpoint = util.get_keyword_value(oauth_decorator.keywords, "authorize_endpoint")
    token_endpoint = util.get_keyword_value(oauth_decorator.keywords, "token_endpoint")

    if not authorize_endpoint or not token_endpoint:
        return

    url_arguments = list(set(uritemplate.variables(authorize_endpoint)).union(set(uritemplate.variables(token_endpoint))))
    if parsed_docstring:
        docstring_params = [param.name for param in parsed_docstring.params]

        missing_args_in_docstring = [url_arg for url_arg in url_arguments if url_arg not in docstring_params]
        if missing_args_in_docstring:
            checker.add_message("book-oauth-params-missing", args=(node.repr_name(), ", ".join(missing_args_in_docstring)), node=node)

        extra_args_in_docstring = [docstring_arg for docstring_arg in docstring_params if docstring_arg not in url_arguments]
        if extra_args_in_docstring:
            checker.add_message("book-oauth-extra-params-in-doc", args=(node.repr_name(), ", ".join(extra_args_in_docstring)), node=node)


class BookChecker(BaseChecker):
    """
    BookChecker class checks if a class is a book by looking for a specific decorator. It also
    checks if the book has the required documentation block, description, and author.
    """

    name = "kognitos-book-checker"
    msgs = {
        "C7301": (  # message id
            # template of displayed message
            "Book %s is missing description",
            # message symbol
            "book-missing-description",
            # message description
            "All books must have a description",
        ),
        "C7302": (  # message id
            # template of displayed message
            "Book %s is missing author",
            # message symbol
            "book-missing-author",
            # message description
            "All books must have an author",
        ),
        "C7303": (  # message id
            # template of displayed message
            "Book %s is missing documentation",
            # message symbol
            "book-missing-documentation",
            # message description
            "All books must have a documentation block attached to them",
        ),
        "C7304": (  # message id
            # template of displayed message
            "Unable to parse documentation block for book %s",
            # message symbol
            "book-bad-documentation",
            # message description
            "All books must have a correct documentation string attached to them",
        ),
        "C7305": (  # message id
            # template of displayed message
            "Book '%s' has a bad name",
            # message symbol
            "book-bad-name",
            # message description
            "All book must have a single noun phrase as their name",
        ),
        "C7306": (  # message id
            # template of displayed message
            "Path '%s' does not exist for book icon",
            # message symbol
            "book-bad-icon-path",
            # message description
            "All book must have a valid icon path",
        ),
        "C7307": (  # message id
            # template of displayed message
            "Icon path '%s' must have a .svg extension",
            # message symbol
            "book-bad-icon-extension",
            # message description
            "All book must have a valid '.svg' icon path",
        ),
        "C7308": (  # message id
            # template of displayed message
            "Book '%s' has a bad noun phrase",
            # message symbol
            "book-bad-noun-phrase",
            # message description
            "All book must have a single noun phrase as their noun phrase",
        ),
        "C7309": (  # message id
            # template of displayed message
            "Book '%s' does not follow class name convention",
            # message symbol
            "book-bad-class-name",
            # message description
            "Book classes must end with the word `Book`. For example: `InterestingBook`.",
        ),
        "C7310": (  # message id
            # template of displayed message
            "Method %s require valid authentication method for book",
            # message symbol
            "book-missing-authentication-method",
            # message description
            "A method with connection required must have valid authentication method in the book",
        ),
        "C7311": (  # message id
            # template of displayed message
            "The method must not be named as '%s'",
            # message symbol
            "book-forbidden-method-name",
            # message description
            "A method named '%s' is forbidden inside book as it leads to silent conflicts.",
        ),
        "C7312": (  # message id
            # template of displayed message
            "Book '%s' is missing the following blueprint procedure implementation: %s",
            # message symbol
            "book-missing-blueprint-procedure-implementation",
            # message description
            "Book has missing blueprint procedure implementation",
        ),
        "C7313": (  # message id
            # template of displayed message
            "Procedure has missing blueprint procedure input concept '%s'",
            # message symbol
            "book-missing-blueprint-procedure-input-concept",
            # message description
            "A blueprint procedure must have the same input concepts as the book procedure",
        ),
        "C7314": (  # message id
            # template of displayed message
            "Procedure has an unexpected extra input concept '%s'. All fields which are not present in the blueprint must be Optional",
            # message symbol
            "book-unexpected-blueprint-procedure-input-concept",
            # message description
            "A blueprint procedure must have the same input concepts as the book procedure. Extra inputs must be Optional",
        ),
        "C7315": (  # message id
            # template of displayed message
            "Procedure has wrong blueprint procedure input concept type '%s'",
            # message symbol
            "book-wrong-blueprint-procedure-input-concept-type",
            # message description
            "A blueprint procedure must have the same input concepts as the book procedure",
        ),
        "C7316": (  # message id
            # template of displayed message
            "Procedure has missing blueprint procedure output concept '%s'",
            # message symbol
            "book-missing-blueprint-procedure-output-concept",
            # message description
            "A blueprint procedure must have the same output concepts as the book procedure",
        ),
        "C7317": (  # message id
            # template of displayed message
            "Procedure has wrong blueprint procedure output concept type for output '%s'",
            # message symbol
            "book-wrong-blueprint-procedure-output-concept-type",
            # message description
            "A blueprint procedure must have the same output concepts as the book procedure",
        ),
        "C7318": (  # message id
            # template of displayed message
            "Book '%s' is missing oauthtoken handler. Add a function decorated with `@oauthtoken` to handle the oauth token",
            # message symbol
            "book-missing-oauthtoken-handler",
            # message description
            "A book that supports oauth must have a function decorated with @oauthtoken to handle the oauth token",
        ),
        "C7319": (  # message id
            # template of displayed message,
            "The oauthtoken handler is missing the required argument '%s' of type '%s'",
            # message symbol
            "oauthtoken-handler-missing-arg",
            # message description
            "The oauthtoken handler must have the required arguments",
        ),
        "C7320": (
            # template of displayed message
            "The oauthtoken handler has a wrong argument type '%s' it should be '%s'",
            # message symbol
            "oauthtoken-handler-wrong-arg-type",
            # message description
            "The oauthtoken handler must have the required arguments",
        ),
        "C7321": (
            # template of displayed message
            "The oauthtoken handler has an unexpected argument '%s'",
            # message symbol
            "oauthtoken-handler-unexpected-arg",
            # message description
            "The oauthtoken handler must have the required arguments",
        ),
        "C7322": (  # message id
            # template of displayed message
            "Book %s is missing description for OAuth params %s",
            # message symbol
            "book-oauth-params-missing",
            # message description
            "All books with OAuth support must have a description for the OAuth params",
        ),
        "C7323": (  # message id
            # template of displayed message
            "Book %s has additional OAuth params in the description %s",
            # message symbol
            "book-oauth-extra-params-in-doc",
            # message description
            "All books with OAuth support must have a description for the OAuth params",
        ),
        "C7324": (  # message id
            # template of displayed message
            "Missing 'name' argument in @book decorator (class name %s)",
            # message symbol
            "book-missing-name-argument",
            # message description
            "The @book decorator must have a 'name' argument",
        ),
        "C7325": (  # message id
            # template of displayed message
            "Book %s has @discover functions but no @invoke functions",
            # message symbol
            "book-discover-missing-invoke",
            # message description
            "Books with @discover functions must also have @invoke functions",
        ),
        "C7326": (  # message id
            # template of displayed message
            "Book %s has @invoke functions but no @discover functions",
            # message symbol
            "book-invoke-missing-discover",
            # message description
            "Books with @invoke functions must also have @discover functions",
        ),
        "C7327": (  # message id
            # template of displayed message
            "Book %s has multiple @discover functions, only one is allowed",
            # message symbol
            "book-multiple-discover-functions",
            # message description
            "Books can have at most one @discover function",
        ),
        "C7328": (  # message id
            # template of displayed message
            "Book %s has multiple @invoke functions, only one is allowed",
            # message symbol
            "book-multiple-invoke-functions",
            # message description
            "Books can have at most one @invoke function",
        ),
        "C7329": (  # message id
            # template of displayed message
            "Book %s is missing tags parameter in @book decorator",
            # message symbol
            "book-missing-tags",
            # message description
            "All books must have tags parameter in the @book decorator",
        ),
        "C7330": (  # message id
            # template of displayed message
            "Book %s tags are not following naming conventions. Should be capitalized - tags: [%s]",
            # message symbol
            "tags-bad-naming",
            # message description
            "All tags should be capitalized",
        ),
        "C7331": (  # message id
            # template of displayed message
            "Book %s has tags parameter that is not a list",
            # message symbol
            "book-tags-not-list",
            # message description
            "The tags parameter in @book decorator must be a list",
        ),
        "C7332": (  # message id
            # template of displayed message
            "Book %s has implements the @discover mechanism but has no @discoverable function",
            # message symbol
            "book-missing-discoverable-functions",
            # message description
            "Books that implement the @discover mechanism must have @discoverable functions that returns a list of discoverable entities.",
        ),
        "C7333": (  # message id
            # template of displayed message
            "Book %s has multiple @discoverable functions, only one is allowed",
            # message symbol
            "book-multiple-discoverable-functions",
            # message description
            "Books can have at most one @discoverable function",
        ),
    }

    def __init__(
        self,
        linter: PyLinter,
        book_rule_factory: BookRuleFactory = DefaultBookRuleFactory(),
    ) -> None:
        super().__init__(linter)
        self._has_authentication_method = False
        self._is_connect_exist = False
        self._is_procedure_exist = False
        self._supports_oauth = False
        self.rules = book_rule_factory.get_rules()

    @classmethod
    def is_book(cls, node: nodes.ClassDef) -> bool:
        return bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.book_decorator.book"))

    @classmethod
    def supports_oauth(cls, node: nodes.ClassDef) -> bool:
        return bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.oauth_decorator.oauth"))

    @classmethod
    def book_name(cls, node: nodes.ClassDef):
        decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.book_decorator.book")

        if decorator and hasattr(decorator, "keywords") and len(decorator.keywords) > 0:
            name_keyword = next(filter(lambda x: x.arg == "name", decorator.keywords), None)

            if name_keyword:
                return next(name_keyword.value.infer()).value

        return None

    @classmethod
    def book_icon(cls, node: nodes.ClassDef):
        decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.book_decorator.book")

        if decorator and hasattr(decorator, "keywords") and len(decorator.keywords) > 0:
            name_keyword = next(filter(lambda x: x.arg == "icon", decorator.keywords), None)

            if name_keyword:
                return next(name_keyword.value.infer()).value
        return None

    @classmethod
    def book_noun_phrase(cls, node: nodes.ClassDef):
        decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.book_decorator.book")

        if decorator and hasattr(decorator, "keywords") and len(decorator.keywords) > 0:
            name_keyword = next(filter(lambda x: x.arg == "noun_phrase", decorator.keywords), None)

            if name_keyword:
                return next(name_keyword.value.infer()).value

        return None

    @classmethod
    def book_blueprints(cls, node: nodes.ClassDef):
        bases = node.bases
        blueprints = [base for base in bases if util.get_decorator_by_name(util._infer_class(base), "kognitos.bdk.decorators.blueprint_decorator.blueprint")]
        return blueprints

    @classmethod
    def blueprint_procedures_from_classdef(cls, node: nodes.ClassDef):
        return util.get_functions_by_decorator_from_classdef(node, "kognitos.bdk.decorators.blueprint_decorator.blueprint_procedure")

    @classmethod
    def procedures_from_classdef(cls, node: nodes.ClassDef):
        return util.get_functions_by_decorator_from_classdef(node, "kognitos.bdk.decorators.procedure_decorator.procedure")

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        if BookChecker.is_book(node):
            self._is_connect_exist = util.check_if_decorator_exists(node, "connect")
            self._is_procedure_exist = util.check_if_decorator_exists(node, "procedure")

            # check that the book has a single noun phrase as its name
            book_name = BookChecker.book_name(node)
            self._has_authentication_method = util.check_authentication_method(node)

            if book_name:
                try:
                    noun_phrases, _ = KlangParser.parse_noun_phrases(book_name)
                    if len(noun_phrases) > 1:
                        self.add_message("book-bad-name", args=book_name, node=node)
                except SyntaxError:
                    self.add_message("book-bad-name", args=book_name, node=node)
            else:
                self.add_message("book-missing-name-argument", args=node.repr_name(), node=node)

            book_name = book_name or node.repr_name()

            if not node.repr_name().endswith("Book"):
                self.add_message("book-bad-class-name", args=node.repr_name(), node=node)

            # check that the book has a valid icon path
            icon_path = BookChecker.book_icon(node)

            if icon_path:
                file_path = node.root().file or ""
                path_to_book = os.path.dirname(file_path)
                full_path_to_icon = os.path.join(path_to_book, icon_path)
                if not os.path.exists(full_path_to_icon):
                    self.add_message("book-bad-icon-path", args=icon_path, node=node)

                if not icon_path.endswith(".svg"):
                    self.add_message("book-bad-icon-extension", args=icon_path, node=node)

            # check noun_phrase
            noun_phrase = BookChecker.book_noun_phrase(node)

            if noun_phrase:
                try:
                    noun_phrases, _ = KlangParser.parse_noun_phrases(noun_phrase)
                    if len(noun_phrases) > 1:
                        self.add_message("book-bad-noun-phrase", args=book_name, node=node)
                except SyntaxError:
                    self.add_message("book-bad-noun-phrase", args=book_name, node=node)

            # check that it has a doc block

            try:
                parsed_docstring = None if not node.doc_node else DocstringParser().parse(node.doc_node.value)

            except DocstringParseError:
                self.add_message(
                    "book-bad-documentation",
                    args=node.repr_name(),
                    node=node.doc_node,
                )
                parsed_docstring = None

            if not node.doc_node:
                self.add_message("book-missing-documentation", args=node.repr_name(), node=node)
            elif parsed_docstring:
                # check short description
                if parsed_docstring.short_description:
                    short_description = parsed_docstring.short_description.strip()
                    if not short_description:
                        self.add_message(
                            "book-missing-description",
                            args=node.repr_name(),
                            node=node.doc_node,
                        )
                else:
                    self.add_message(
                        "book-missing-description",
                        args=node.repr_name(),
                        node=node.doc_node,
                    )

                # check author
                author = parsed_docstring.author
                if not author:
                    self.add_message(
                        "book-missing-author",
                        args=node.repr_name(),
                        node=node.doc_node,
                    )

                check_blueprints(self, node)

            if BookChecker.supports_oauth(node):
                self._supports_oauth = True
                check_oauth_params_in_docstring(self, node, parsed_docstring)
                if not util.check_if_decorator_exists(node, "oauthtoken"):
                    self.add_message("book-missing-oauthtoken-handler", args=node.repr_name(), node=node)

            for rule in self.rules:
                rule.check_rule(linter=self.linter, node=node)

    def visit_functiondef(self, node: nodes.FunctionDef | nodes.AsyncFunctionDef) -> None:
        connect_decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.connect_decorator.connect")
        procedure_decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.procedure_decorator.procedure")
        authtoken_decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.oauthtoken_decorator.oauthtoken")

        if node.name == "connect" and self._is_connect_exist and not connect_decorator:
            self.add_message("book-forbidden-method-name", node=node, args=node.name)
            return

        if node.name == "procedure" and self._is_procedure_exist:
            self.add_message("book-forbidden-method-name", node=node, args=node.name)
            return

        if procedure_decorator and util.check_connection_required(node):
            if not self._has_authentication_method:
                self.add_message(
                    "book-missing-authentication-method",
                    args=node.name,
                    node=node,
                )

        if authtoken_decorator:
            index, access_token_arg = next(filter(lambda index_arg: index_arg if index_arg[1].name == "access_token" else None, enumerate(node.args.arguments)), (None, None))

            if access_token_arg:
                annotation = node.args.annotations[index]  # type: ignore
                if not (util.is_str_type(annotation) and not util.is_optional_type(annotation)):
                    self.add_message("oauthtoken-handler-wrong-arg-type", node=annotation, args=(annotation.as_string(), "str"))
            else:
                self.add_message("oauthtoken-handler-missing-arg", node=node, args=("access_token", "str"))

            index, expires_in_arg = next(filter(lambda index_arg: index_arg if index_arg[1].name == "expires_in" else None, enumerate(node.args.arguments)), (None, None))

            if expires_in_arg:
                annotation = node.args.annotations[index]  # type: ignore
                if not (util.is_int_type(annotation) and util.is_optional_type(annotation)):
                    self.add_message("oauthtoken-handler-wrong-arg-type", node=annotation, args=(annotation.as_string(), "Optional[int]"))
            else:
                self.add_message("oauthtoken-handler-missing-arg", node=node, args=("expires_in", "Optional[int]"))

            extra_args = [arg for arg in node.args.arguments if arg.name not in ["access_token", "expires_in", "self"]]

            for extra_arg in extra_args:
                self.add_message("oauthtoken-handler-unexpected-arg", node=node, args=(extra_arg.name,))

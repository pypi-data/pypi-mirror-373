import itertools
from typing import List, Optional, Tuple

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

from kognitos.bdk.docstring import (DocstringConcept, DocstringParam,
                                    DocstringParseError, DocstringParser)
from kognitos.bdk.errors import SignatureError
from kognitos.bdk.klang.parser import KlangParser
from kognitos.bdk.reflection import (BookProcedureDescriptor,
                                     BookProcedureSignature,
                                     ConnectionRequired)
from kognitos.bdk.reflection.factory import BookProcedureFactory

from .. import util
from ..util import get_hint_message
from .procedure_rule_factory import (DefaultProcedureRuleFactory,
                                     ProcedureRuleFactory)


def get_all_input_names(node: nodes.FunctionDef | nodes.AsyncFunctionDef, book_procedure: BookProcedureDescriptor) -> List[str]:
    """
    Retrieves all input concept names as snake case, as well as all the function arguments which are not mapped to any input concept.
    """
    concept_map = {p.python_name: [c.noun_phrases[0].to_snake_case() for c in p.concepts] for p in book_procedure.parameter_concept_map}
    input_names = itertools.chain.from_iterable(concept_map.values())
    func_args = [arg.name for arg in node.args.arguments if arg.name != "self" and arg.name not in concept_map]

    return func_args + list(input_names)


class ProcedureChecker(BaseChecker):
    """
    ProcedureChecker

    This class is responsible for checking the documentation and type annotations of procedures.
    """

    name = "kognitos-procedure-checker"
    msgs = {
        "C7401": (  # message id
            # template of displayed message
            "Procedure %s is missing description",
            # message symbol
            "procedure-missing-description",
            # message description
            "All procedures must have a description",
        ),
        "C7403": (  # message id
            # template of displayed message
            "Procedure %s is missing documentation",
            # message symbol
            "procedure-missing-documentation",
            # message description
            "All procedures must have a documentation block attached to them",
        ),
        "C7404": (  # message id
            # template of displayed message
            "Unable to parse documentation block for procedure %s: %s",
            # message symbol
            "procedure-bad-documentation",
            # message description
            "All procedures must have a correct documentation string attached to them",
        ),
        "C7405": (  # message id
            # template of displayed message
            "Missing type annotations for arg %s",
            # message symbol
            "procedure-argument-missing-type-annotation",
            # message description
            "All procedures must have all of their arguments annotated with type",
        ),
        "C7406": (  # message id
            # template of displayed message
            "Unsupported type for arg %s. %s",
            # message symbol
            "procedure-argument-unsupported-type",
            # message description
            "BCI supports a limited set of types",
        ),
        "C7407": (  # message id
            # template of displayed message
            "Unable to infer type for arg %s",
            # message symbol
            "procedure-argument-cannot-infer-type",
            # message description
            "Internal Error. Unable to infer the type for the argument.",
        ),
        "C7408": (  # message id
            # template of displayed message
            "Missing description for arg %s",
            # message symbol
            "procedure-missing-argument-description",
            # message description
            "All arguments must have a description",
        ),
        "C7409": (  # message id
            # template of displayed message
            "Cannot parse english for procedure %s: %s",
            # message symbol
            "procedure-cannot-parse-english",
            # message description
            "All procedure english sentences must use a well defined format",
        ),
        "C7410": (  # message id
            # template of displayed message
            "Unsupported type for return %s. %s",
            # message symbol
            "procedure-return-unsupported-type",
            # message description
            "BCI supports a limited set of types",
        ),
        "C7411": (  # message id
            # template of displayed message
            "Unable to infer type for return %s",
            # message symbol
            "procedure-return-cannot-infer-type",
            # message description
            "Internal Error. Unable to infer the type for the return type.",
        ),
        "C7412": (  # message id
            # template of displayed message
            "Missing english sentence for procedure %s",
            # message symbol
            "procedure-missing-english",
            # message description
            "All @procedure must include the english signature",
        ),
        "C7413": (  # message id
            # template of displayed message
            "Missing description for return of method %s",
            # message symbol
            "procedure-missing-return-description",
            # message description
            "All returns must have a description",
        ),
        "C7414": (  # message id
            # template of displayed message
            "The method %s returns something, but it isn't declared on the english sentence",
            # message symbol
            "procedure-missing-return",
            # message description
            "All returns must be explicitly declared on the english sentence",
        ),
        "C7415": (  # message id
            # template of displayed message
            "The method %s has more than one filter expression",
            # message symbol
            "procedure-invalid-filter-expression-count",
            # message description
            "A method can have at most one filter expression",
        ),
        "C7416": (  # message id
            # template of displayed message
            "The method %s must return a List of values",
            # message symbol
            "procedure-with-filter-expression-must-return-list",
            # message description
            "A method with a filter expression must return a List of values",
        ),
        "C7417": (  # message id
            # template of displayed message
            "The method argument %s must be of type Optional[int]",
            # message symbol
            "procedure-with-pagination-type-mismatch",
            # message description
            "A method which supports pagination must use Optional[int] for the offset and limit parameters",
        ),
        "C7418": (  # message id
            # template of displayed message
            "The method %s is missing pagination parameters",
            # message symbol
            "procedure-missing-pagination-parameters",
            # message description
            "A method which supports pagination must include both offset and limit parameters",
        ),
        "C7419": (  # message id
            # template of displayed message
            "The method %s must return a List[T] or Optional[List[T]]",
            # message symbol
            "procedure-with-pagination-return-type-mismatch",
            # message description
            "A method which supports pagination must return a List[T] or Optional[List[T]]",
        ),
        "C7420": (  # message id
            "The method %s has an PoS argument (%s) which is a Tuple, but the length of the Tuple types does not match the length of the English signature PoS",
            # message symbol
            "procedure-pos-argument-tuple-length-mismatch",
            # message description
            "The length of the Tuple does not match the length of the English signature",
        ),
        "C7421": (  # message id
            "The method '%s' has a description for argument '%s' which is not in the English signature",
            # message symbol
            "procedure-bad-argument-description",
            # message description
            "The argument in the description is not part of the English signature",
        ),
        "C7422": (  # message id
            "Question return type-hints must specify the noun phrases of what is being asked for and the type of the expected answer. %s",
            # message symbol
            "procedure-question-unspecified-type",
            # message description
            "You cannot use Question as a return type without specifying the inner parameters of said question.",
        ),
        "C7423": (  # message id
            "Bad typing on Question. You need to have a string literal (parseable as noun phrases) as the first parameter, and a supported type as the second parameter. %s",
            # message symbol
            "procedure-question-bad-type",
            # message description
            "There is either a problem with the type or format of the first parameter (should be a string literal representing the noun phrases), or the second parameter is not a supported type.",
        ),
        "C7424": (  # message id
            "Bad typing on Question. The first parameter should be a literal string parseable as noun phrases. %s",
            # message symbol
            "procedure-question-bad-noun-phrases",
            # message description
            "The first parameter or a question type-hint should be a literal string parseable as noun phrases.",
        ),
        "C7425": (  # message id
            "Function with @discover decorator must have a 'what' parameter of type str",
            # message symbol
            "discover-missing-what-parameter",
            # message description
            "All functions with @discover decorator must have a 'what' parameter of type str",
        ),
        "C7426": (  # message id
            "Function with @discover decorator must return List[BookProcedureDescriptor]",
            # message symbol
            "discover-invalid-return-type",
            # message description
            "All functions with @discover decorator must return List[BookProcedureDescriptor]",
        ),
        "C7427": (  # message id
            "Function with @invoke decorator must have a 'procedure_id' parameter of type str",
            # message symbol
            "invoke-missing-procedure-id-parameter",
            # message description
            "All functions with @invoke decorator must have a 'procedure_id' parameter of type str",
        ),
        "C7428": (  # message id
            "Procedure %s is missing examples",
            # message symbol
            "procedure-missing-examples",
            # message description
            "All procedures must include at least one example",
        ),
        "C7429": (  # message id
            "@discoverables function is missing parameter '%s' of type %s",
            # message symbol
            "discoverables-missing-parameter",
            # message description
            "The @discoverables function must have 'search', 'limit', and 'offset' parameters",
        ),
        "C7430": (  # message id
            "@discoverables function must return List[Discoverable]",
            # message symbol
            "discoverables-invalid-return-type",
            # message description
            "The @discoverables function must return List[Discoverable]",
        ),
        "C7431": (  # message id
            "Default values defined in the @discoverables function's arguments will not be considered. Handle them in the function's code.",
            # message symbol
            "discoverables-has-default-values",
            # message description
            "Default values not allowed on @discoverables function's arguments.",
        ),
        "C7432": (  # message id
            "Procedure %s 'connection_required' keyword must be an Enum",
            # message symbol
            "connection_required-invalid-type",
            # message description
            "The keyword connection_required value must be a ConnectionRequired Enum",
        ),
    }

    def __init__(self, linter: PyLinter, procedure_rule_factory: ProcedureRuleFactory = DefaultProcedureRuleFactory()) -> None:
        super().__init__(linter)
        self.rules = procedure_rule_factory.get_rules()

    @classmethod
    def is_procedure(cls, node: nodes.FunctionDef):
        return bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.procedure_decorator.procedure"))

    @classmethod
    def procedure_english(cls, node: nodes.FunctionDef) -> Optional[str]:
        decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.procedure_decorator.procedure")

        if decorator and hasattr(decorator, "args") and len(decorator.args) > 0:
            return next(decorator.args[0].infer()).value

        return None

    def visit_functiondef(self, node: nodes.FunctionDef | nodes.AsyncFunctionDef) -> None:
        if ProcedureChecker.is_procedure(node):
            # check if the english of the procedure is correct
            english_sentence = ProcedureChecker.procedure_english(node)
            if not english_sentence:
                self.add_message("procedure-missing-english", node=node, args=node.name)
                return

            try:
                english_signature = BookProcedureSignature.from_parser_signature(KlangParser.parse_signature(english_sentence))
            except SyntaxError as error:
                self.add_message("procedure-cannot-parse-english", node=node, args=[node.name, str(error)])
                return

            # verify parameters
            process_pagination_parameters(self, node)
            message_count, filter_expressions = process_input_parameters(self, english_signature, node)

            if filter_expressions and (not node.returns or not util.is_list_type(node.returns)):
                self.add_message("procedure-with-filter-expression-must-return-list", args=node.repr_name(), node=node)
            elif node.returns:
                invalid_return_nodes = util.get_invalid_type_nodes_for_procedure_outputs(node.returns)

                for n in invalid_return_nodes:
                    hint = get_hint_message(n)
                    self.add_message("procedure-return-unsupported-type", args=(n.repr_name(), hint), node=n)
                    message_count = message_count + 1

                question_nodes = util.extract_question_nodes(node.returns)
                for qnode in question_nodes:
                    if not (hasattr(qnode, "slice") and hasattr(qnode.slice, "elts")):
                        hint = "Questions cannot be type-hinted without declaring the sub-parameters. They should be declared as 'Question[Literal['noun phrase'], type]'."
                        self.add_message("procedure-question-unspecified-type", args=(hint,), node=qnode)
                        message_count = message_count + 1
                        continue

                    subtypes = qnode.slice.elts
                    if len(subtypes) != 2:
                        hint = f"The question typehint is not correctly formatted, as it has the wrong number of parameters (has {len(subtypes)}, should have 2). The proper format is 'Question[Literal['noun phrase'], type]'."
                        self.add_message("procedure-question-bad-type", args=(hint,), node=qnode)
                        message_count = message_count + 1
                        continue

                    hint = get_hint_message(qnode)
                    if not util.is_literal_noun_phrases_string_type(subtypes[0]):
                        self.add_message("procedure-question-bad-noun-phrases", args=(hint,), node=qnode)
                        message_count = message_count + 1
                    if util.get_invalid_type_nodes(subtypes[1], depth=0, seen=None):
                        self.add_message("procedure-question-bad-type", args=(hint,), node=qnode)
                        message_count = message_count + 1

                if not util.extract_non_question_nodes(node.returns) and question_nodes:
                    hint = "A procedure cannot always return a question. If it does not have results, typehint 'None | <QUESTION/S>' instead."
                    self.add_message("procedure-return-unsupported-type", args=(node.repr_name(), hint), node=node.returns)
                    message_count = message_count + 1

            if message_count > 0:
                return

            # extract signature
            python_signature = util.create_signature(node)

            # parse docstring
            if not node.doc_node:
                self.add_message("procedure-missing-documentation", node=node)
                return

            try:
                docstring = DocstringParser.parse(node.doc_node.value)
            except DocstringParseError as error:
                self.add_message("procedure-bad-documentation", node=node.doc_node, args=[node.name, str(error)])
                return

            # create procedure
            try:
                book_procedure = BookProcedureFactory.create(node.name, english_signature, python_signature, docstring, override_connection_required=ConnectionRequired.NEVER)
            except SignatureError as error:
                if util.is_tuple_arguments_mismatch_error(error):
                    self.add_message(
                        "procedure-missing-return",
                        args=node.repr_name(),
                        node=node,
                    )
                return

            if not book_procedure.short_description and not book_procedure.long_description:
                self.add_message(
                    "procedure-missing-description",
                    args=node.repr_name(),
                    node=node.doc_node,
                )

            for parameter in book_procedure.parameter_concept_map:
                reserved_noun_phrases = ["limit", "offset"]
                argument = [arg for arg in node.args.arguments if arg.name == parameter.python_name][0]
                for concept in parameter.concepts:
                    if not concept.description and parameter.python_name not in reserved_noun_phrases:
                        self.add_message(
                            "procedure-missing-argument-description",
                            args=parameter.python_name,
                            node=argument,
                        )

            if book_procedure.outputs:
                for output in book_procedure.outputs:
                    if not output.description:
                        self.add_message(
                            "procedure-missing-return-description",
                            args=node.repr_name(),
                            node=node,
                        )

                outputs_length = len(book_procedure.outputs)
                if (outputs_length in [0, 1]) and util.is_tuple_type(node.returns):
                    self.add_message(
                        "procedure-missing-return",
                        args=node.repr_name(),
                        node=node,
                    )
                elif outputs_length > 1 and not util.is_tuple_type(node.returns):
                    self.add_message(
                        "procedure-missing-return",
                        args=node.repr_name(),
                        node=node,
                    )

            self.check_for_invalid_input_concepts(docstring.input_concepts, node)

            function_inputs = get_all_input_names(node, book_procedure)
            docstring_inputs = self._get_docstring_input(docstring.input_concepts, docstring.params)

            extra_doc_concepts = sorted(set(docstring_inputs) - set(function_inputs))
            for extra_doc_concept in extra_doc_concepts:
                self.add_message("procedure-bad-argument-description", args=(node.repr_name(), extra_doc_concept), node=node)

            for rule in self.rules:
                rule.check_rule(linter=self.linter, book_procedure=book_procedure, node=node)

        # Not handled as a ProcedureRule due to being a specific case where it's not a procedure.
        # We can see about opening up the set of rules for these cases in the future
        check_discover_rule(self, node)

    def visit_asyncfunctiondef(self, node: nodes.AsyncFunctionDef) -> None:
        self.visit_functiondef(node)

    def _get_docstring_input(self, input_concepts: list[DocstringConcept], params: List[DocstringParam]):
        return [noun_phrase.to_snake_case() for input_concept in input_concepts for noun_phrase in getattr(input_concept, "noun_phrases", None) or []] + [
            param.name for param in params
        ]  # Both input concepts and arguments

    def check_for_invalid_input_concepts(self, input_concepts: list[DocstringConcept], node: nodes.FunctionDef | nodes.AsyncFunctionDef):
        for input_concept in input_concepts:
            if not input_concept.noun_phrases:
                self.add_message("procedure-bad-argument-description", args=(node.repr_name(), input_concept.name), node=node)


def process_pagination_parameters(procedure_checker: ProcedureChecker, node: nodes.FunctionDef | nodes.AsyncFunctionDef):

    pagination_arg_names = ["offset", "limit"]
    args_and_annotations = [(arg, node.args.annotations[idx]) for idx, arg in enumerate(node.args.arguments) if arg.name in pagination_arg_names]

    if not args_and_annotations:
        return

    if len(args_and_annotations) != len(pagination_arg_names):
        present_arg_names = [arg.name for (arg, _) in args_and_annotations]

        for name in pagination_arg_names:
            if name not in present_arg_names:
                procedure_checker.add_message("procedure-missing-pagination-parameters", args=name, node=node)

    for arg, annotation in args_and_annotations:
        # All pagination parameters must be of type Optional[int]
        if not (util.is_int_type(annotation) and util.is_optional_type(annotation)):
            procedure_checker.add_message("procedure-with-pagination-type-mismatch", args=arg.name, node=node)

    if not util.is_list_type(node.returns):
        procedure_checker.add_message("procedure-with-pagination-return-type-mismatch", node=node)


def process_input_parameters(procedure_checker: ProcedureChecker, english_signature: BookProcedureSignature, node: nodes.FunctionDef | nodes.AsyncFunctionDef) -> Tuple[int, int]:
    """
    Processes the input parameters of a procedure and returns the number of messages and the number of filter expressions.
    """
    message_count = 0
    filter_expressions_count = 0

    for idx, argument in enumerate(node.args.arguments):
        arg_name = argument.repr_name()
        if arg_name == "self":
            continue

        annotation = node.args.annotations[idx]
        if annotation is None:
            procedure_checker.add_message(
                "procedure-argument-missing-type-annotation",
                args=arg_name,
                node=argument,
            )
            message_count = message_count + 1
        else:
            is_filter_expression = util.is_filter_expression_type(annotation)
            if is_filter_expression:
                filter_expressions_count += 1

            if is_filter_expression and filter_expressions_count > 1:
                procedure_checker.add_message(
                    "procedure-invalid-filter-expression-count",
                    args=arg_name,
                    node=argument,
                )

            if not is_filter_expression:
                # NOTE: This is a special scenario where we allow top-level Tuple input type
                # if we're targetting the PoS object or target.
                if arg_name in ("object", "target") and util.is_tuple_type(annotation):
                    annotation_nodes = annotation.slice.elts

                    if arg_name == "object":
                        input_length_matches = len(annotation_nodes) == len(english_signature.object or [])
                    else:
                        input_length_matches = len(annotation_nodes) == len(english_signature.target or [])

                    if not input_length_matches:
                        procedure_checker.add_message(
                            "procedure-pos-argument-tuple-length-mismatch",
                            args=arg_name,
                            node=argument,
                        )
                        continue

                    for ann_node in annotation_nodes:
                        invalid_nodes = util.get_invalid_type_nodes(ann_node, depth=0, seen=None)
                        if any(invalid_nodes):
                            hint = get_hint_message(ann_node)
                            procedure_checker.add_message(
                                "procedure-argument-unsupported-type",
                                args=(node.repr_name(), hint),
                                node=ann_node,
                            )
                            message_count = message_count + 1

                else:
                    invalid_type_nodes = util.get_invalid_type_nodes(annotation, depth=0, seen=None)

                    if any(invalid_type_nodes):
                        hint = get_hint_message(annotation)
                        procedure_checker.add_message(
                            "procedure-argument-unsupported-type",
                            args=(node.repr_name(), arg_name if not hint else arg_name + ": " + hint),
                            node=argument,
                        )
                        message_count = message_count + 1

    return message_count, filter_expressions_count


def check_discover_rule(checker: ProcedureChecker, node: nodes.FunctionDef | nodes.AsyncFunctionDef) -> None:
    """Check @discover and @invoke decorator requirements"""
    has_discover = bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.discover_decorator.discover"))
    has_invoke = bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.invoke_decorator.invoke"))
    has_discoverables = bool(util.get_decorator_by_name(node, "kognitos.bdk.decorators.discoverables_decorator.discoverables"))

    if has_discover:
        # Check if function has 'what' parameter of type str
        what_param = None
        for i, arg in enumerate(node.args.arguments):
            if arg.name == "what":
                annotation = node.args.annotations[i] if i < len(node.args.annotations) else None
                what_param = (arg, annotation)
                break

        if not what_param:
            checker.add_message("discover-missing-what-parameter", node=node)
        else:
            arg, annotation = what_param
            if annotation is None or not util.is_str_type(annotation):
                checker.add_message("discover-missing-what-parameter", node=arg)

        # Check return type is List[BookProcedureDescriptor]
        if node.returns:
            if not util.node_annotation_is_list_of(node.returns, "kognitos.bdk.reflection.book_procedure_descriptor.BookProcedureDescriptor"):
                checker.add_message("discover-invalid-return-type", node=node.returns)
        else:
            checker.add_message("discover-invalid-return-type", node=node)

    if has_invoke:
        # Check if function has 'procedure_id' parameter of type str
        procedure_id_param = None
        for i, arg in enumerate(node.args.arguments):
            if arg.name == "procedure_id":
                annotation = node.args.annotations[i] if i < len(node.args.annotations) else None
                procedure_id_param = (arg, annotation)
                break

        if not procedure_id_param:
            checker.add_message("invoke-missing-procedure-id-parameter", node=node)
        else:
            arg, annotation = procedure_id_param
            if annotation is None or not util.is_str_type(annotation):
                checker.add_message("invoke-missing-procedure-id-parameter", node=arg)

    if has_discoverables:
        # Check for mandatory arguments: search: Optional[str], limit: Optional[int], offset: Optional[int]
        required_args = {
            "search": ("Optional[str]", lambda ann: ann is not None and util.is_optional_type(ann) and util.is_str_type(ann)),
            "limit": ("Optional[int]", lambda ann: ann is not None and util.is_optional_type(ann) and util.is_int_type(ann)),
            "offset": ("Optional[int]", lambda ann: ann is not None and util.is_optional_type(ann) and util.is_int_type(ann)),
        }

        found_args = {name: False for name in required_args}
        for i, arg in enumerate(node.args.arguments):
            if arg.name in required_args:
                expected_type, check_fn = required_args[arg.name]
                annotation = node.args.annotations[i]
                if check_fn(annotation):
                    found_args[arg.name] = True

        for name, found in found_args.items():
            expected_type, _ = required_args[name]
            if not found:
                checker.add_message("discoverables-missing-parameter", args=(name, expected_type), node=node)

        if node.args.defaults:
            checker.add_message("discoverables-has-default-values", args=None, node=node)

        if node.returns:
            if not util.node_annotation_is_list_of(node.returns, "kognitos.bdk.api.discoverable.Discoverable"):
                checker.add_message("discoverables-invalid-return-type", node=node.returns)
        else:
            checker.add_message("discoverables-invalid-return-type", node=node)

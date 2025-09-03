import datetime
import inspect
import itertools
from dataclasses import dataclass
from typing import IO, Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import astroid
from astroid import InferenceError, NameInferenceError, nodes
from astroid.typing import SuccessfulInferenceResult

from kognitos.bdk.api import ConnectionRequired, FilterExpression
from kognitos.bdk.api.noun_phrase import NounPhrase
from kognitos.bdk.decorators import concept
from kognitos.bdk.docstring import DocstringParser
from kognitos.bdk.klang import KlangParser
from kognitos.bdk.reflection import (BookProcedureDescriptor,
                                     BookProcedureSignature)
from kognitos.bdk.reflection.factory import BookProcedureFactory


def _infer_class(node: SuccessfulInferenceResult) -> nodes.ClassDef:
    if hasattr(node, "value") and node.value is not None:
        inferred_node = next(node.value.infer())
    else:
        inferred_node = next(node.infer())
    return inferred_node  # type: ignore [reportArgumentType]


def type_check_connect(annotation_node):
    if isinstance(annotation_node, astroid.Const) and annotation_node.value is None:
        return True

    try:
        if hasattr(annotation_node, "value"):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except NameInferenceError:
        return False

    if inferred_node == astroid.Uninferable:
        return False

    if inferred_node.qname() == "builtins.str":
        return True

    if inferred_node.qname() == "kognitos.bdk.typing.sensitive.Sensitive":
        return type_check_connect(annotation_node.slice)

    return False


def get_hint_message(annotation_node):
    """Returns a hint message if the annotation involves a Table, ArrayStream type, or a Question."""
    try:
        if (hasattr(annotation_node, "qname") and annotation_node.qname() == "kognitos.bdk.api.questions.Question") or next(
            annotation_node.infer()
        ).qname() == "kognitos.bdk.api.questions.Question":
            return "Questions cannot be directly used as a concept type. If you are type-hinting a procedure to indicate that it can return a question, use a union type at the top level of the return type-hint. If the procedure can return a question, but has no results, use 'None | Question[Literal['noun phrase'], type]' as the return type-hint."
    except (InferenceError, NameInferenceError):
        pass

    if isinstance(annotation_node, astroid.Name):
        if annotation_node.name == "Table":
            return "If you are trying to use Table, make sure to import either pyarrow and declare it as pyarrow.Table, or import arro3.core and declare it as arro3.core.Table"
        if annotation_node.name == "ArrayStream":
            return "If you are trying to use ArrayStream, make sure to import nanoarrow and declare it as nanoarrow.ArrayStream"
    return ""


def concept_unset_instance(node: nodes.ClassDef) -> Optional[astroid.bases.Instance]:
    """
    Gets the value of the `unset` instance if the keyword is set on the @concept decorator
    """
    decorator = get_concept_decorator(node)

    if decorator:
        if hasattr(decorator, "keywords") and len(decorator.keywords) > 0:
            unset_keyword = next(filter(lambda x: x.arg == "unset", decorator.keywords), None)
            if unset_keyword:
                return next(unset_keyword.value.infer())

    return None


def get_invalid_type_nodes(annotation_node, depth=0, seen=None, unset: Optional[astroid.bases.Instance] = None, allow_questions: bool = False) -> List[nodes.NodeNG]:
    """
    Given an `annotation_node` recursively checks for valid types.

    NOTE: The types checked in this function are the ones that are supported by the API for both inputs and outputs.
    Not all types are covered here! There are some special scenarios just like outputs, which also support top-level tuple returns.

    Arguments:
        annotation_node: the node to be evaluated
        depth: the depth at which we're evaluating the type check
        seen: A set of node qnames which have already been successfully evaluated
        unset: The value of the unset instance scoped to the concept being analyzed
        allow_questions: Whether to consider Question types as valid (default: False).

    Returns:
        A list nodes which have invalid types
    """

    def add_seen(node):
        type_name = node.qname()

        if seen is None:
            return {type_name}

        seen.add(type_name)
        return seen

    if isinstance(annotation_node, astroid.Const) and annotation_node.value is None:
        return []

    if isinstance(annotation_node, astroid.BinOp):
        return get_invalid_type_nodes(annotation_node.left, allow_questions=allow_questions) + get_invalid_type_nodes(annotation_node.right, allow_questions=allow_questions)

    if isinstance(annotation_node, astroid.Attribute) and hasattr(annotation_node, "attrname"):
        if (
            annotation_node.attrname == "Table"
            and isinstance(annotation_node.expr, astroid.Attribute)
            and annotation_node.expr.attrname == "core"
            and isinstance(annotation_node.expr.expr, astroid.Name)
            and annotation_node.expr.expr.name == "arro3"
        ):
            return []

        try:
            full_name = annotation_node.as_string()
            if full_name in ["pyarrow.Table", "nanoarrow.ArrayStream", "arro3.core.Table"]:
                return []
        except (AttributeError, TypeError):
            pass

        if annotation_node.attrname in ["Table", "ArrayStream"]:
            return [annotation_node]

    try:
        if hasattr(annotation_node, "value") and isinstance(annotation_node.value, nodes.NodeNG):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except NameInferenceError:
        return [annotation_node]

    if inferred_node == astroid.Uninferable:
        return [annotation_node]

    if isinstance(inferred_node, nodes.ClassDef):
        unset_instance = concept_unset_instance(inferred_node) or unset
    else:
        unset_instance = unset

    simple_type_checks = [
        "builtins.str",
        "builtins.float",
        "builtins.int",
        "builtins.bool",
        "builtins.bytes",
        "datetime.datetime",
        "_pydatetime.datetime",
        "datetime.date",
        "_pydatetime.date",
        "datetime.time",
        "_pydatetime.time",
        "typing.IO",
        "typing.Any",
        "kognitos.bdk.api.noun_phrase.NounPhrase",
        "kognitos.bdk.api.filter.FilterExpression",
        "uuid.UUID",
        "abc.ABC",
    ]

    if unset_instance is not None:
        simple_type_checks.append(unset_instance.qname())

    # Avoid infinite recursion
    if seen and inferred_node.qname() in seen:
        return []

    if inferred_node.qname() in simple_type_checks:
        return []
    if inferred_node.qname() in ("typing.Dict", "builtins.dict"):
        key_type, value_type = annotation_node.slice.elts
        if _infer_class(key_type).qname() == "builtins.str":
            return get_invalid_type_nodes(value_type, depth, add_seen(inferred_node))

        return [annotation_node]
    if is_enum(inferred_node):
        # Peek first element and ensure it's a valid type
        return get_invalid_type_nodes(inferred_node.body[0], depth, seen, unset=unset_instance)
    if inferred_node.qname() == "kognitos.bdk.typing.sensitive.Sensitive":
        return get_invalid_type_nodes(annotation_node.slice, depth, seen, unset=unset_instance)
    if inferred_node.qname() in ("typing.Optional", "typing.List", "builtins.list"):
        return get_invalid_type_nodes(annotation_node.slice, depth, seen, unset=unset_instance)
    if inferred_node.qname() == "typing.Union":
        annotation_nodes = annotation_node.slice.elts
        return list(
            itertools.chain(
                *[
                    get_invalid_type_nodes(annotation_node, depth + 1, add_seen(inferred_node), unset=unset_instance, allow_questions=allow_questions)
                    for annotation_node in annotation_nodes
                ]
            )
        )

    # # Handle attr.field type declarations
    if inferred_node.qname() == "attr._make._CountingAttr" and hasattr(annotation_node, "func") and annotation_node.func.name == "field":
        type_kwarg = next(filter(lambda kwarg: kwarg.arg == "type", getattr(annotation_node, "keywords", [])), None)
        if type_kwarg:
            return get_invalid_type_nodes(type_kwarg.value, depth=depth, seen=seen)
        return [annotation_node]

    if isinstance(inferred_node, astroid.ClassDef) and ((is_concept(inferred_node) and depth == 0) or is_dataclass_or_attrs(inferred_node) and depth > 0):
        if is_dataclass_or_attrs(inferred_node):
            fields_and_annotations = get_dataclass_fields_and_annotations_recursive(inferred_node)
            return list(
                itertools.chain(
                    *[get_invalid_type_nodes(annotation_node, depth + 1, add_seen(inferred_node), unset=unset_instance) for _, annotation_node in fields_and_annotations]
                )
            )

        return []

    if inferred_node.qname() == "kognitos.bdk.api.questions.Question" and allow_questions:
        return []

    return [annotation_node]


def extract_non_question_nodes(annotation_node) -> List[nodes.NodeNG]:
    try:
        if hasattr(annotation_node, "value") and isinstance(annotation_node.value, nodes.NodeNG):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except (InferenceError, NameInferenceError):
        return [annotation_node]

    if inferred_node.qname() == "kognitos.bdk.api.questions.Question":
        return []

    if inferred_node.qname() == "typing.Union":
        non_question_nodes = []
        for node in annotation_node.slice.elts:
            non_question_nodes.extend(extract_non_question_nodes(node))
        return non_question_nodes

    if inferred_node.qname() == "builtins.UnionType":
        return extract_non_question_nodes(annotation_node.left) + extract_non_question_nodes(annotation_node.right)

    return [annotation_node]


def extract_question_nodes(annotation_node) -> List[nodes.NodeNG]:
    try:
        if hasattr(annotation_node, "value") and isinstance(annotation_node.value, nodes.NodeNG):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except (InferenceError, NameInferenceError):
        return []

    if inferred_node.qname() == "kognitos.bdk.api.questions.Question":
        return [annotation_node]

    if inferred_node.qname() == "typing.Union":
        question_nodes = []
        for node in annotation_node.slice.elts:
            question_nodes.extend(extract_question_nodes(node))
        return question_nodes

    if inferred_node.qname() == "builtins.UnionType":
        return extract_question_nodes(annotation_node.left) + extract_question_nodes(annotation_node.right)

    return []


def is_noun_phrases_string(value: str) -> bool:
    nps, _ = KlangParser.parse_noun_phrases(value)
    nps_to_string = noun_phrases_to_string([NounPhrase.from_tuple(np) for np in nps])
    return nps_to_string == value


def is_literal_noun_phrases_string_type(annotation_node):
    if not hasattr(annotation_node, "value"):
        return False

    inferred_node = next(annotation_node.value.infer())
    if not inferred_node.qname() == "typing.Literal":
        return False

    if not (hasattr(annotation_node, "slice") and hasattr(annotation_node.slice, "value")):
        return False

    literal_value = annotation_node.slice.value
    if not (isinstance(literal_value, str) and is_noun_phrases_string(literal_value)):
        return False

    return True


def get_invalid_type_nodes_for_procedure_outputs(annotation_node) -> List[nodes.NodeNG]:
    """
    Checks for invalid types for procedure outputs. If the top-level return is a tuple, it will check each element of the tuple.
    Otherwise, it will check the top-level return by leveraging the `get_invalid_type_nodes` function.

    Returns:
        A list of top-level invalid nodes.
    """
    try:
        if is_tuple_type(annotation_node):
            nodes_to_check = annotation_node.slice.elts
            invalid_nodes = []
            for n in nodes_to_check:
                if any(get_invalid_type_nodes(n, depth=0, seen=None)):
                    invalid_nodes.append(n)
            return invalid_nodes
    except (InferenceError, NameInferenceError) as e:
        if isinstance(e, InferenceError) and "StopIteration" in str(e):
            return []
        return []

    if any(get_invalid_type_nodes(annotation_node, depth=0, seen=None, allow_questions=True)):
        return [annotation_node]

    return []


def is_filter_expression_type(annotation_node) -> bool:
    try:
        if hasattr(annotation_node, "value"):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except (InferenceError, NameInferenceError) as e:
        if isinstance(e, InferenceError) and "StopIteration" in str(e):
            return False
        return False

    if inferred_node == astroid.Uninferable:
        return False

    if inferred_node.qname() == "kognitos.bdk.api.filter.FilterExpression":
        return True

    if inferred_node.qname() == "typing.Optional":
        return is_filter_expression_type(annotation_node.slice)

    return False


def is_tuple_type(annotation_node) -> bool:
    try:
        inferred_node = _infer_class(annotation_node)
    except (InferenceError, NameInferenceError) as e:
        if isinstance(e, InferenceError) and "StopIteration" in str(e):
            return False
        return False

    return inferred_node.qname() == "typing.Tuple"


def is_list_type(annotation_node) -> bool:
    try:
        if hasattr(annotation_node, "value"):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except NameInferenceError:
        return False

    if inferred_node.qname() in ("typing.List", "builtins.list"):
        return True

    if inferred_node.qname() == "typing.Optional":
        return is_list_type(annotation_node.slice)

    return False


def is_int_type(annotation_node) -> bool:
    try:
        if hasattr(annotation_node, "value"):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except NameInferenceError:
        return False

    if inferred_node.qname() == "builtins.int":
        return True

    if inferred_node.qname() == "typing.Optional":
        return is_int_type(annotation_node.slice)

    return False


def is_str_type(annotation_node) -> bool:
    try:
        inferred_node = _infer_class(annotation_node)
    except NameInferenceError:
        return False

    if inferred_node.qname() == "builtins.str":
        return True

    if inferred_node.qname() == "typing.Optional":
        return is_str_type(annotation_node.slice)

    return False


def is_optional_type(annotation_node) -> bool:
    try:
        if hasattr(annotation_node, "value"):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except NameInferenceError:
        return False

    if inferred_node.qname() == "typing.Optional":
        return True

    return False


def get_decorator_by_name(node: Union[nodes.FunctionDef, nodes.ClassDef], decorator_name: str) -> Optional[nodes.NodeNG]:
    if node.decorators:
        for decorator in node.decorators.nodes:
            try:
                if hasattr(decorator, "func") and decorator.func:
                    func = next(decorator.func.infer())
                else:
                    func = next(decorator.infer())

                if func.qname() == decorator_name:
                    return decorator

            except NameInferenceError:
                continue

    return None


def get_functions_by_decorator_from_classdef(node: nodes.ClassDef, decorator_name: str) -> list[nodes.FunctionDef]:
    """
    Given a class definition, find all functions that have a given decorator.
    """
    return [function for function in node.body if isinstance(function, nodes.FunctionDef) and get_decorator_by_name(function, decorator_name)]


def is_enum(node: SuccessfulInferenceResult | Any) -> bool:
    if isinstance(node, nodes.ClassDef):
        return any(b.name == "Enum" for b in node.bases if hasattr(b, "name"))

    return False


def is_abstract(node: SuccessfulInferenceResult) -> bool:
    abstract_bases = [base for base in node.bases if _infer_class(base).qname() == "abc.ABC"]
    return any(abstract_bases)


def get_class_assignments(node: nodes.ClassDef) -> List[nodes.AnnAssign]:
    return [child for child in node.body if isinstance(child, nodes.AnnAssign) and child.target]


def get_dataclass_decorator(node: nodes.ClassDef) -> Optional[nodes.NodeNG]:
    return get_decorator_by_name(node, "dataclasses.dataclass")


def get_attrs_decorator(node: nodes.ClassDef) -> Optional[nodes.NodeNG]:
    return get_decorator_by_name(node, "attr._next_gen.define")


def is_dataclass_or_attrs(node: nodes.ClassDef) -> bool:
    """Checks if the node is a dataclass or attrs and if it inherits from all dataclasses or attrs"""
    if node.bases:
        is_abstract_class = is_abstract(node)

        if is_abstract_class:
            return True

        concrete_node_bases = node.bases if not is_abstract_class else []
    else:
        concrete_node_bases = []

    is_dataclass_or_attrs_ = bool(get_attrs_decorator(node)) or bool(get_dataclass_decorator(node))
    return is_dataclass_or_attrs_ and all(map(lambda n: is_dataclass_or_attrs(_infer_class(n)), concrete_node_bases))


def get_dataclass_field_names_recursive(node: nodes.ClassDef) -> List[str]:
    """Gets all the fields of a dataclass and the fields of its parent dataclasses"""
    fields = []

    for child in node.body:
        if isinstance(child, nodes.AnnAssign) and child.target:
            field_name = child.target.name
            fields.append(field_name)

    for base in node.bases:
        fields.extend(get_dataclass_field_names_recursive(_infer_class(base)))

    return fields


def get_dataclass_fields_and_annotations_recursive(node: nodes.ClassDef) -> List[tuple[Union[nodes.AnnAssign, nodes.Assign], nodes.NodeNG]]:
    """Gets the fields and annotations of a dataclass and its parent dataclasses"""
    fields = []

    bases_to_ignore = [
        "abc.ABC",
    ]

    for child in node.body:
        if isinstance(child, nodes.AnnAssign) and child.target:
            fields.append((child, child.annotation))
        elif isinstance(child, nodes.Assign) and child.targets:
            fields.append((child, child.value))

    for base in node.bases:
        inferred_base = _infer_class(base)
        if inferred_base.qname() not in bases_to_ignore:
            fields.extend(get_dataclass_fields_and_annotations_recursive(inferred_base))

    return fields


def get_missing_attributes_in_docstring(field_names: List[str], docstring: str) -> List[str]:
    """
    Gets the missing attributes in a docstring
    """

    def get_attribute_from_doc(field_name, docstring_attributes):
        for att in docstring_attributes:
            if att.name == field_name and att.description:
                return att

        return None

    missing_attributes = []
    parser = DocstringParser()
    parsed_docstring = parser.parse(docstring)

    for field_name in field_names:
        att = get_attribute_from_doc(field_name, parsed_docstring.attributes)
        if not att:
            missing_attributes.append(field_name)

    return missing_attributes


def is_partial_dataclass_or_attrs(node: nodes.ClassDef) -> bool:
    """Checks if a node is a dataclass but does not inherit from all dataclasses, or if a node inherits from datacalsses but is not a dataclass"""

    is_dataclass_or_attrs_ = bool(get_attrs_decorator(node)) or bool(get_dataclass_decorator(node))

    # node is a dataclass or attrs but does not inherit from all dataclasses or attrs
    if is_dataclass_or_attrs_ and not all(map(lambda n: is_dataclass_or_attrs(_infer_class(n)), node.bases)):
        return True

    # node inherits from at least one dataclass or attrs but is not a dataclass or attrs
    if not is_dataclass_or_attrs_ and any(map(lambda n: is_dataclass_or_attrs(_infer_class(n)), node.bases)):
        return True

    return False


def get_partial_dataclass_or_attrs(node: nodes.ClassDef) -> List[str]:
    """Return the partial dataclass or attrs for a node"""

    partial_classes = []
    for base_class in node.bases:
        if not is_dataclass_or_attrs(_infer_class(base_class)):
            partial_classes.append(base_class.repr_name())

    return partial_classes


def get_concept_decorator(node: nodes.ClassDef) -> Optional[nodes.NodeNG]:
    return get_decorator_by_name(node, "kognitos.bdk.decorators.concept_decorator.concept")


def is_concept(node: nodes.ClassDef) -> bool:
    return bool(get_concept_decorator(node))


def check_authentication_method(node: nodes.ClassDef) -> bool:
    """
    Checks if a class has an OAuth decorator or a function with the @connect decorator.
    Args:
        node: The Astroid ClassDef node to check.

    Returns:
        True if authentication methods are present, False otherwise.
    """
    if get_decorator_by_name(node, "kognitos.bdk.decorators.oauth_decorator.oauth"):
        return True

    for member in node.body:
        if isinstance(member, nodes.FunctionDef):
            if get_decorator_by_name(member, "kognitos.bdk.decorators.connect_decorator.connect"):
                return True

    return False


def check_if_decorator_exists(node: nodes.ClassDef, decorator: str) -> bool:
    for member in node.body:
        if isinstance(member, nodes.FunctionDef):
            decorator_name = ""
            if decorator == "connect":
                decorator_name = "kognitos.bdk.decorators.connect_decorator.connect"
            if decorator == "procedure":
                decorator_name = "kognitos.bdk.decorators.procedure_decorator.procedure"
            if decorator == "oauthtoken":
                decorator_name = "kognitos.bdk.decorators.oauthtoken_decorator.oauthtoken"

            if get_decorator_by_name(member, decorator_name):
                return True

    return False


def check_connection_required(node: nodes.FunctionDef) -> bool:
    """
    Checks if a function has the @procedure decorator with connection_required=ConnectionRequired.ALWAYS.
    Args:
        node: The Astroid FunctionDef node to check.

    Returns:
        True if connection_required is ALWAYS, False otherwise.
    """
    decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.procedure_decorator.procedure")
    if decorator:
        for keyword in decorator.keywords:
            if keyword.arg == "connection_required":
                expr = keyword.value.expr.name
                value = keyword.value.attrname
                return f"{expr}.{value}" == str(ConnectionRequired.ALWAYS)
    return False


def get_field_and_class_name(node: Union[nodes.AnnAssign, nodes.Assign]) -> Tuple[str, str]:
    if isinstance(node, nodes.AnnAssign):
        field_name: str = node.target.name  # type: ignore [reportOptionalMemberAccess]
        class_name: str = node.parent.name  # type: ignore [reportOptionalMemberAccess]
    else:
        field_name: str = node.targets[0].name  # type: ignore [reportOptionalMemberAccess]
        class_name: str = node.parent.name  # type: ignore [reportOptionalMemberAccess]

    return field_name, class_name


def get_first_assign_parent(node: Optional[nodes.NodeNG]) -> Optional[Union[nodes.Assign, nodes.AnnAssign]]:

    if not node:
        return None
    if isinstance(node, (nodes.AnnAssign, nodes.Assign)):
        return node

    return get_first_assign_parent(node.parent)


def annotate(annotation_node):
    if annotation_node is None:
        return None

    inferred_node = None

    try:
        if hasattr(annotation_node, "value") and isinstance(annotation_node.value, nodes.NodeNG):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except (InferenceError, NameInferenceError) as e:
        if isinstance(e, InferenceError) and "StopIteration" in str(e):
            return False
        return False

    if inferred_node is None:
        return None

    if inferred_node == astroid.Uninferable:
        return None

    if inferred_node.qname() == "builtins.NoneType":
        return None

    if inferred_node.qname() == "kognitos.bdk.api.filter.FilterExpression":
        return FilterExpression

    if inferred_node.qname() == "builtins.int":
        return int

    if inferred_node.qname() == "builtins.float":
        return float

    if inferred_node.qname() == "builtins.bool":
        return bool

    if inferred_node.qname() == "builtins.bytes":
        return bytes

    if inferred_node.qname() == "builtins.str":
        return str

    if inferred_node.qname() in ("datetime.datetime", "_pydatetime.datetime"):
        return datetime.datetime

    if inferred_node.qname() in ("datetime.date", "_pydatetime.date"):
        return datetime.date

    if inferred_node.qname() in ("datetime.time", "_pydatetime.time"):
        return datetime.time

    if inferred_node.qname() == "typing.IO":
        return IO

    if inferred_node.qname() == "typing.Any":
        return Any

    if inferred_node.qname() == "uuid.UUID":
        return UUID

    if inferred_node.qname() == "kognitos.bdk.api.noun_phrase.NounPhrase":
        return NounPhrase

    if inferred_node.qname() == "typing.Optional":
        return Optional[annotate(annotation_node.slice)]

    if inferred_node.qname() == "typing.Union":
        if isinstance(annotation_node.slice, nodes.Tuple):
            return Union[*[annotate(el) for el in annotation_node.slice.elts]]  # type: ignore [reportInvalidTypeForm]

        return Union[annotate(annotation_node.slice)]

    if inferred_node.qname() == "typing.Tuple":
        if isinstance(annotation_node.slice, nodes.Tuple):
            return Tuple[*[annotate(el) for el in annotation_node.slice.elts]]  # type: ignore [reportInvalidTypeForm]

        return Union[annotate(annotation_node.slice)]

    if inferred_node.qname() in ("typing.Dict", "builtins.dict"):
        key_type, value_type = annotation_node.slice.elts
        return Dict[annotate(key_type), annotate(value_type)]

    if inferred_node.qname() in ("typing.List", "builtins.list"):
        return List[annotate(annotation_node.slice)]

    if isinstance(inferred_node, nodes.ClassDef) and is_dataclass_or_attrs(inferred_node):
        decorator = get_concept_decorator(inferred_node)
        is_a_keyword = decorator.keywords[0]  # type: ignore [reportOptionalMemberAccess]

        if isinstance(is_a_keyword.value, nodes.List):
            is_a = [next(el.infer()).value for el in is_a_keyword.value.elts]
        else:
            is_a = is_a_keyword.value.value

        return dataclass(concept(is_a=is_a)(type(inferred_node.name, (object,), {"__doc__": "This is for annotation purposes only"})))

    return None


def create_signature(function_node: nodes.FunctionDef) -> inspect.Signature:
    parameters = []

    if function_node.args and function_node.args.args:
        for idx, arg in enumerate(function_node.args.args):
            if arg.name in function_node.args.kwonlyargs:
                kind = inspect.Parameter.KEYWORD_ONLY
            else:
                kind = inspect.Parameter.POSITIONAL_OR_KEYWORD

            param = inspect.Parameter(name=arg.name, kind=kind, annotation=annotate(function_node.args.annotations[idx]))

            parameters.append(param)

    return inspect.Signature(parameters, return_annotation=annotate(function_node.returns))


def create_procedure_descriptor(function_node: nodes.FunctionDef) -> BookProcedureDescriptor:
    python_signature = create_signature(function_node)
    decorator = get_decorator_by_name(function_node, "kognitos.bdk.decorators.procedure_decorator.procedure")
    english_signature = BookProcedureSignature.from_parser_signature(KlangParser.parse_signature(decorator.args[0].value))  # type: ignore [reportOptionalMemberAccess]
    if not function_node.doc_node:
        raise ValueError("Missing Function docstring")
    docstring = DocstringParser.parse(function_node.doc_node.value)  # type: ignore [reportOptionalMemberAccess]
    return BookProcedureFactory.create(
        function_node.name,
        english_signature,
        python_signature,
        docstring,
        override_connection_required=ConnectionRequired.NEVER,
    )


def create_blueprint_procedure_descriptor(function_node: nodes.FunctionDef) -> BookProcedureDescriptor:
    python_signature = create_signature(function_node)
    decorator = get_decorator_by_name(function_node, "kognitos.bdk.decorators.blueprint_decorator.blueprint_procedure")
    english_signature = BookProcedureSignature.from_parser_signature(KlangParser.parse_signature(decorator.args[0].value))  # type: ignore [reportOptionalMemberAccess]
    if not function_node.doc_node:
        raise ValueError("Missing Function docstring")
    docstring = DocstringParser.parse(function_node.doc_node.value)  # type: ignore [reportOptionalMemberAccess]
    return BookProcedureFactory.create(
        function_node.name,
        english_signature,
        python_signature,
        docstring,
        override_connection_required=ConnectionRequired.NEVER,
    )


def noun_phrases_to_string(noun_phrases: List[NounPhrase]) -> str:
    return "'s ".join([str(np) for np in noun_phrases])


def is_tuple_arguments_mismatch_error(error):
    return str(error) == "The number of elements in the return tuple do not match the number of outputs in the english signature"


def get_keyword_value(keywords, arg_name):
    """
    Helper function to get the value of a keyword argument by name.

    Args:
        keywords: List of keyword arguments from a decorator
        arg_name (str): Name of the argument to find

    Returns:
        The value of the keyword argument if found, None otherwise
    """
    keyword = next((kw for kw in keywords if kw.arg == arg_name), None)
    if keyword and hasattr(keyword.value, "value"):
        return keyword.value.value
    return None


def node_annotation_is_list_of(annotation_node, type_name: str) -> bool:
    """Check if the annotation is List of the given type."""
    try:
        if hasattr(annotation_node, "value"):
            inferred_node = next(annotation_node.value.infer())
        else:
            inferred_node = next(annotation_node.infer())
    except NameInferenceError:
        return False

    if inferred_node == astroid.Uninferable:
        return False

    # Check if it's List or typing.List
    if inferred_node.qname() not in ("typing.List", "builtins.list"):
        return False

    # Check if the slice is BookProcedureDescriptor
    if not hasattr(annotation_node, "slice"):
        return False

    try:
        if hasattr(annotation_node.slice, "value"):
            slice_inferred = next(annotation_node.slice.value.infer())
        else:
            slice_inferred = next(annotation_node.slice.infer())
    except NameInferenceError:
        return False

    return slice_inferred.qname() == type_name

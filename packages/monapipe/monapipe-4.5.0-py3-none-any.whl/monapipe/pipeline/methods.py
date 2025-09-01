# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import base64
import warnings
from typing import Any, List, Optional, Tuple, Type, Union

import dill
import spacy_alignments as tokenizations
from spacy.language import Language
from spacy.tokens import Doc, Span, Token


def add_extension(obj: Union[Type[Doc], Type[Span], Type[Token]], name: str, default: Any = None):
    """Add a custom extension to a spacy class.

    Args:
        obj: The spacy class.
        name: The name of the attribute.
        default: The default value of the attribute.

    """
    try:
        obj.set_extension(name, default=default)
    except ValueError:
        # the extension already exists
        pass


def get_alignments(doc: Doc, custom_tokens: List[str]) -> Tuple[List[List[int]], List[List[int]]]:
    """Make alignments between document tokenization and custom tokenization.

    Args:
        doc: The document.
        custom_tokens: List of tokens, potentially differently tokenized than in the document.

    Returns:
        Mapping from document index to custom indices.
        Mapping from custom index to document indices.

    """
    doc_tokens = [token.text for token in doc]
    return tokenizations.get_alignments(doc_tokens, custom_tokens)


def get_doc_text(doc: Doc, normalized: bool = False) -> str:
    """Return the full text of a document.
        (Takes into account the changes of normalizer and slicer.)

    Args:
        doc: The document.
        normalized: If True, return the normalised text; if False, return the original text.

    Returns:
        str: The text of the document.

    """
    if (not normalized) and hasattr(doc._, "text"):
        return doc._.text
    if hasattr(doc._, "fulltext"):
        return doc._.fulltext
    return doc.text


def optional(component: Any, nlp: Language, names: List[str]):
    """Checks whether pipeline components are added and raises a warning otherwise.

    Args:
        component: The current pipeline components.
        nlp: The pipeline object.
        names: A list of names of components.
            To not result in a warning, each name in `names` has to match a name in `nlp.pipe_names`,
            where matching is done with `pipe_name.endswith(name)`.

    """
    component_name = component.__class__.__name__
    for name in names:
        pipe_name_exists = False
        for pipe_name in nlp.pipe_names:
            if pipe_name == name or pipe_name.endswith("_" + name):
                pipe_name_exists = True
                break
        if not pipe_name_exists:
            warnings.warn("No " + name + " added before " + component_name + ".", UserWarning)


def requires(component: Any, nlp: Language, names: List[str]):
    """Checks whether pipeline components are added and raises an error otherwise.

    Args:
        component: The current pipeline components.
        nlp: The pipeline object.
        names: A list of names of components.
            To not result in an error, each name in `names` has to match a name in `nlp.pipe_names`,
            where matching is done with `pipe_name.endswith(name)`.

    """
    component_name = component.__class__.__name__
    for name in names:
        pipe_name_exists = False
        for pipe_name in nlp.pipe_names:
            if pipe_name == name or pipe_name.endswith("_" + name):
                pipe_name_exists = True
                break
        if not pipe_name_exists:
            raise ValueError("No " + name + " added before " + component_name + ".")


def serialize_config_param(obj: Any) -> str:
    """Make a pipeline component config paramter's value JSON-serializable.

    Args:
        obj: The object to serialize.

    Returns:
        A string representation of the object.

    """
    return base64.b64encode(dill.dumps(obj))


def deserialize_config_param(obj: Union[str, Any]) -> Any:
    """Restore a pipeline component config paramter's value that was serialized with `serialize_config_param`.

    Args:
        obj: The object to deserialize.

    Returns:
        The original object.

    """
    try:
        return dill.loads(base64.b64decode(obj))
    except TypeError:
        # the object is already deserialized
        return obj


def update_token_span_groups(doc: Doc, names: Optional[List[str]] = None):
    """Update the references between `doc.spans` and `token._.spans`.
        This method should be called at the end of a pipeline component that changes `doc.spans`.
        After the update one can call:
            - `token._.spans[name]` instead of `[span for span in doc.spans[name] if token in span]`
            - `token._.span[name]` to get the shortest span from `token._.spans[name]`

    Args:
        doc: The document.
        names: The names of the span groups to update.
            If `None`, all span groups are updated.

    """
    add_extension(Token, "spans", {})
    add_extension(Token, "span", {})
    if names is None:
        names = doc.spans.keys()
        for token in doc:
            token._.spans = {}
            token._.span = {}
    for name in names:
        for token in doc:
            token._.spans[name] = [span for span in doc.spans[name] if token in span]
            try:
                token_spans = sorted(token._.spans[name], key=lambda span: span.end - span.start)
                token._.span[name] = token_spans[0]
            except IndexError:
                token._.span[name] = None

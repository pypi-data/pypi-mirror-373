# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import copy
import pickle
import warnings
from typing import Any, Callable, Set

from spacy.tokens import Doc, DocBin, MorphAnalysis, Span, Token


class PickleToken:
    """Class to replace `Token` during pickling."""

    def __init__(self, token):
        self.i = token.i


class PickleSpan:
    """Class to replace `Span` during pickling."""

    def __init__(self, span):
        self.start = span.start
        self.end = span.end


class PickleMorphAnalysis:
    """Class to replace `MorphAnalysis` during pickling."""

    def __init__(self, morph):
        self.feats = morph.to_dict()


def make_pickleable(doc: Doc, safe: bool = True) -> Doc:
    """Make a `Doc` object pickleable.

    Args:
        doc: The document.
        safe: If True, make sure that the object is really pickleable;
            remove all custom attributes from the document if necessary.

    Returns:
        The document but now its pickleable.

    """
    doc = _convert_doc(doc, _make_obj_pickleable)
    if safe:
        try:
            pickle.dumps(doc)
        except Exception as ex:
            warnings.warn(
                type(ex).__name__ + " occurred during pickling. All custom attributes are removed."
            )
            return list(DocBin(store_user_data=False, docs=[doc]).get_docs(doc.vocab))[0]
    return doc


def unmake_pickleable(doc: Doc) -> Doc:
    """Make a `Doc` object unpickleable.
        Undo the changes from `make_pickleable`.

    Args:
        doc: The document.

    Returns:
        The document as before calling `make_pickleable` on it.

    """
    return _convert_doc(doc, _unmake_obj_pickleable)


def _convert_doc(doc: Doc, conversion_func: Callable[[Any, Doc], Any]) -> Doc:
    """Convert the custom extensions of the document, tokens and spans.

    Args:
        doc: The document.
        conversion_func: `_make_obj_pickleable` or `_unmake_obj_pickleable`.

    Returns:
        The document with converted custom attributes.

    """
    spans = get_built_in_spans(doc)
    for attr in dir(doc._):
        if attr in ["get", "set", "has"]:
            continue
        setattr(doc._, attr, conversion_func(getattr(doc._, attr), doc, spans))
    for token in doc:
        for attr in dir(token._):
            if attr in ["get", "set", "has"]:
                continue
            setattr(token._, attr, conversion_func(getattr(token._, attr), doc, spans))
    seen_spans = set()
    while len(spans) > 0:
        span = spans.pop()
        if span in seen_spans:
            continue
        seen_spans.add(span)
        for attr in dir(span._):
            if attr in ["get", "set", "has"]:
                continue
            setattr(span._, attr, conversion_func(getattr(span._, attr), doc, spans))
    return doc


def _make_obj_pickleable(obj: Any, doc: Doc, spans: Set[Span], depth: int = 0) -> Any:
    """Make an object pickleable by replacing all referenced `Token`s and `Span`s with `PickleToken`s and `PickleSpan`s.

    Args:
        obj: An object.
        doc: The document that contains the object.
        spans: Set of spans that were seen during pickling.
        depth: The current recursion depth.

    Returns:
        A pickleable object.

    """
    if isinstance(obj, Token):
        return PickleToken(obj)
    if isinstance(obj, Span):
        spans.add(obj)
        return PickleSpan(obj)
    if isinstance(obj, MorphAnalysis):
        return PickleMorphAnalysis(obj)
    if isinstance(obj, (list, set, tuple)):
        obj_type = type(obj)
        return obj_type([_make_obj_pickleable(val, doc, spans, depth) for val in obj])
    if isinstance(obj, dict):
        return {
            _make_obj_pickleable(key, doc, depth): _make_obj_pickleable(val, doc, spans, depth)
            for key, val in obj.items()
        }
    else:
        if depth == 0 and hasattr(obj, "__dict__"):
            obj = copy.copy(obj)
            for key, val in vars(obj).items():
                setattr(obj, key, _make_obj_pickleable(val, doc, spans, depth + 1))
        return obj


def _unmake_obj_pickleable(obj: Any, doc: Doc, spans: Set[Span], depth: int = 0) -> Any:
    """Restore the original object by replacing all referenced `PickleToken`s and `PickleSpan`s with `Token`s and `Span`s.

    Args:
        obj: A pickleable object.
        doc: The document that contains the object.
        spans: Set of spans that were seen during de-pickling.
        depth: The current recursion depth.

    Returns:
        The orignal object.

    """
    if isinstance(obj, PickleToken):
        return doc[obj.i]
    if isinstance(obj, PickleSpan):
        spans.add(doc[obj.start : obj.end])
        return doc[obj.start : obj.end]
    if isinstance(obj, PickleMorphAnalysis):
        return MorphAnalysis(doc.vocab, obj.feats)
    if isinstance(obj, (list, set, tuple)):
        obj_type = type(obj)
        return obj_type([_unmake_obj_pickleable(val, doc, spans, depth) for val in obj])
    if isinstance(obj, dict):
        return {
            _unmake_obj_pickleable(key, doc, depth): _unmake_obj_pickleable(val, doc, spans, depth)
            for key, val in obj.items()
        }
    else:
        if depth == 0 and hasattr(obj, "__dict__"):
            obj = copy.copy(obj)
            for key, val in vars(obj).items():
                setattr(obj, key, _unmake_obj_pickleable(val, doc, spans, depth + 1))
        return obj


def get_built_in_spans(doc: Doc) -> Set[Span]:
    """Returns the spans of a document that can be accessed by built-in methods.

    Args:
        doc: The document.

    Returns:
        The built-in spans in a document.

    """
    spans = set()

    # spans from registered span groups
    spans.update(set([span for key in doc.spans for span in doc.spans[key]]))

    # spans from built-in iterators
    try:
        spans.update(set(doc.ents))
    except ValueError:
        pass  # no named entities
    try:
        spans.update(set(doc.noun_chunks))
    except ValueError:
        pass  # no dependency parse
    try:
        spans.update(set(doc.sents))
    except ValueError:
        pass  # no sentence boundaries

    # make sure that there are no `PickleSpan`s in the list
    spans = [doc[span.start : span.end] for span in spans]

    return set(spans)

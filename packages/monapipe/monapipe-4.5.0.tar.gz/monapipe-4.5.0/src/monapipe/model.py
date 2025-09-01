# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Iterator, List, Optional, Tuple, Union

from spacy.lang.de import GermanDefaults
from spacy.lang.de.syntax_iterators import noun_chunks
from spacy.language import Language
from spacy.tokens import Doc, Span

import monapipe.resource_handler as resources


@Language.component("monapipe_ent")
def monapipe_ent(doc: Doc) -> Doc:
    """Wrapper for spacy's built-in `.ents` component for German."""
    spacy_doc = _pipe_doc_with_built_in_spacy_model(doc)
    doc.set_ents([Span(doc, ent.start, ent.end, ent.label_) for ent in spacy_doc.ents])
    return doc


def monapipe_noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Tuple[int, int, int]]:
    """Wrapper for spacy's built-in `.noun_chunks` syntax iterator for German."""
    doc = doclike.doc
    spacy_doc = _pipe_doc_with_built_in_spacy_model(doc)
    for noun_chunk in noun_chunks(spacy_doc):
        yield noun_chunk


def load(
    adjust_ents: bool = True, adjust_noun_chunks: bool = True, disable: Optional[List[str]] = None
) -> Language:
    """Load a spacy model trained for monapipe.
        Since the monapipe model was trained on UD, the `.ents` and `.noun_chunks` attributes don't work properly.
        Per default, these attributes are taken over from the built-in German spacy model.

    Args:
        adjust_ents: Use the `.ents` annotations from the built-in German spacy model.
        adjust_noun_chunks: Use the `.noun_chunks` iterator on the built-in German spacy model.
        disable: Specify pipeline components to remove from pipe.

    Returns:
        The model.

    """
    GermanDefaults.syntax_iterators["noun_chunks"] = (
        monapipe_noun_chunks if adjust_noun_chunks else noun_chunks
    )
    nlp = resources.access("parsing", clear_resource=True)
    if adjust_ents:
        nlp.add_pipe("monapipe_ent", name="ner")
    if disable is not None:
        for component in disable:
            nlp.remove_pipe(component)
    return nlp


def _pipe_doc_with_built_in_spacy_model(doc: Doc) -> Doc:
    """Re-pipe a document with the built-in German spacy model.
        Use the same tokenization and sentence boundaries as in the given document.
        The result is also stored in `doc._._spacy_doc`.

    Args:
        doc: The document.

    Returns:
        The re-piped document.

    """
    if (
        (not hasattr(doc._, "_spacy_doc"))
        or (getattr(doc._, "_spacy_doc") is None)
        or (getattr(doc._, "_spacy_doc").text != doc.text)
    ):
        tokens, spaces = tuple(zip(*[(token.text, token.whitespace_ != "") for token in doc]))
        spacy_nlp = resources.access("spacy_model")
        spacy_doc = Doc(spacy_nlp.vocab, tokens, spaces)
        for spacy_token, token in zip(spacy_doc, doc):
            spacy_token.is_sent_start = token.is_sent_start
        for _, proc in spacy_nlp.pipeline:
            spacy_doc = proc(spacy_doc)
        Doc.set_extension("_spacy_doc", force=True, default=None)
        setattr(doc._, "_spacy_doc", spacy_doc)
    return getattr(doc._, "_spacy_doc")

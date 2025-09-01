# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import pickle
from typing import Any

from spacy.language import Language
from spacy.tokens import Doc

from monapipe.pipeline.methods import add_extension
from monapipe.pipeline.slicer.methods import span_to_doc
from monapipe.pipeline.slicer.slicer import Slicer


@Language.factory(
    "from_start_slicer",
    assigns=Slicer.assigns,
    default_config={"max_units": -1, "units": "sents", "complete_sentences": True},
)
def from_start_slicer(
    nlp: Language, name: str, max_units: int, units: str, complete_sentences: bool
) -> Any:
    """Spacy component implementation.
        Reduces the document to the first `max_units` units.

    Args:
        nlp: Spacy object.
        name: Component name.
        max_units: The document is cut off after the first `max_units` units.
        units: "sents", "tokens" or "chars".
        complete_sentences: If False, cut before the token that contains the threshold character.
                e.g. "This is a sentence. I lik|e it." -> "This is a sentence. I"
            If True, cut after the sentence that contains the threshold character.
                e.g. "This is a sentence. I lik|e it." -> "This is a sentence. I like it."

    Returns:
        `FromStartSlicer`.

    """
    return FromStartSlicer(nlp, max_units, units, complete_sentences)


class FromStartSlicer(Slicer):
    """The class `FromStartSlicer`."""

    def __init__(self, nlp: Language, max_units: int, units: str, complete_sentences: bool):
        if units not in ["chars", "sents", "tokens"]:
            raise ValueError('Units must be "chars", "sents" or "tokens".')

        super().__init__(nlp, max_units, units, complete_sentences)

    def __call__(self, doc: Doc) -> Doc:
        if (self.units == "sents" or self.complete_sentences) and not doc.has_annotation(
            "SENT_START"
        ):
            raise ValueError("`FromStartSlicer` requires the Doc to be sentenced.")
        fulltext = doc.text
        if self.max_units > 0:
            i = len(doc)
            if self.units == "sents":
                sents = list(doc.sents)
                j = min(len(sents), self.max_units)
                i = sents[j - 1].end
            elif self.units == "tokens":
                i = min(len(doc), self.max_units)
                if self.complete_sentences:
                    i = doc[i].sent.end
            elif self.units == "chars":
                i = 0
                for token in doc:
                    i = token.i
                    try:
                        idx = token._.idx
                    except AttributeError:  # doc is not normalized
                        idx = token.idx
                    if idx > self.max_units:
                        if self.complete_sentences:
                            i = token.sent.end
                        break
            span = doc[:i]
            doc = span_to_doc(span)
        doc._.fulltext = fulltext
        return doc

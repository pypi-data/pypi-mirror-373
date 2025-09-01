# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any, Optional

from spacy.language import Language
from spacy.tokens import Doc

from monapipe.lookups import lookup
from monapipe.pipeline.methods import update_token_span_groups
from monapipe.pipeline.speech_tagger.methods import (
    create_speech_segments_from_token_tags,
)
from monapipe.pipeline.speech_tagger.speech_tagger import SpeechTagger


@Language.factory(
    "quotation_marks_speech_tagger",
    assigns=SpeechTagger.assigns,
    default_config={"sentence_level": None, "dockerfile": None, "api_mode": None},
)
def quotation_marks_speech_tagger(
    nlp: Language,
    name: str,
    sentence_level: Optional[bool],
    dockerfile: Optional[str],
    api_mode: Optional[str],
) -> Any:
    """Spacy component implementation.
        Tags tokens and clauses with speech tags.
        Detects only direct speech within (German) quotation marks.

    Args:
        nlp: Spacy object.
        name: Component name.
        sentence_level: Ignored. This parameter exists only for compatibility with `SpeechTagger`.
        dockerfile: Ignored. This parameter exists only for compatibility with `SpeechTagger`.
        api_mode: Ignored. This parameter exists only for compatibility with `SpeechTagger`.

    Returns:
        `QuotationMarksSpeechTagger`.

    """
    return QuotationMarksSpeechTagger(nlp, sentence_level, dockerfile, api_mode)


class QuotationMarksSpeechTagger(SpeechTagger):
    """The class `QuotationMarksSpeechTagger`."""

    def __init__(
        self,
        nlp: Language,
        sentence_level: Optional[bool],
        dockerfile: Optional[str],
        api_mode: Optional[str],
    ):
        super().__init__(nlp, sentence_level, dockerfile, api_mode)

    def __call__(self, doc: Doc) -> Doc:
        q_marks = lookup(doc.lang_, "quotation_marks")

        offset = -1
        for i, token in enumerate(doc):
            token._.speech = {}
            if token.text in q_marks[0] and (offset < 0 or token.text not in q_marks[1]):
                offset = i
                mark = token.text
            elif token.text in q_marks[1]:
                if offset > -1 and q_marks[1].index(token.text) == q_marks[0].index(mark):
                    for tok in doc[offset : i + 1]:
                        tok._.speech["direct"] = 1.0
                offset = -1

        create_speech_segments_from_token_tags(doc, ["direct"])

        update_token_span_groups(doc, ["speech"])

        return doc

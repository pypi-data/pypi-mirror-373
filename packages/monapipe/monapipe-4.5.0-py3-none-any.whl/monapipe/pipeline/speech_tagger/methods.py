# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import List

from spacy.tokens import Doc

from monapipe.lookups import lookup


def create_speech_segments_from_token_tags(doc: Doc, speech_types: List[str]):
    """Create span-level speech tags from token-level speech tags.

    Args:
        doc: A document whose tokens already have a `_.speech` attribute.
        speech_types: List of speech tags.

    """
    q_marks = lookup(doc.lang_, "quotation_marks")
    doc.spans["speech"] = []
    for speech_type in speech_types:
        current_speech_tokens = []
        current_speech_score = 0.0
        for k, token in enumerate(doc):
            if speech_type in token._.speech:
                current_speech_tokens.append(token)
                current_speech_score += token._.speech[speech_type]
                if (
                    k == len(doc) - 1
                    or (speech_type not in doc[k + 1]._.speech)
                    or (
                        speech_type == "direct"
                        and token.text in q_marks[1]
                        and doc[k + 1].text in q_marks[0]
                    )
                ):  # the last part of the condition assures that two adjacent direct-speech segments are not merged
                    start, end = current_speech_tokens[0].i, current_speech_tokens[-1].i + 1
                    current_speech_span = doc[start:end]
                    current_speech_score /= len(current_speech_tokens)
                    current_speech_span._.speech[speech_type] = current_speech_score
                    if current_speech_span not in doc.spans["speech"]:
                        doc.spans["speech"].append(current_speech_span)
                    current_speech_tokens = []
                    current_speech_score = 0.0

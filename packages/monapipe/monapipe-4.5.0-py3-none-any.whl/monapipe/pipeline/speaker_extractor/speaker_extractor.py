# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Span

from monapipe.pipeline.methods import add_extension


class SpeakerExtractor:
    """Component super class `SpeakerExtractor`."""

    assigns = {
        "span._.addressee": "speech_span._.addressee",
        "span._.speaker": "speech_span._.speaker",
    }

    def __init__(self, nlp: Language):
        add_extension(Span, "addressee")
        add_extension(Span, "speaker")

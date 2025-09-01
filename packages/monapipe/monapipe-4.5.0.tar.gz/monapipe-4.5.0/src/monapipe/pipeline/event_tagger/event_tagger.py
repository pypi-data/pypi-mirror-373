# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Optional

from spacy.language import Language
from spacy.tokens import Span

from monapipe.pipeline.methods import add_extension


class EventTagger:
    """Component super class `EventTagger`."""

    assigns = {"span._.event": "clause._.event"}

    def __init__(self, nlp: Language, dockerfile: Optional[str], api_mode: Optional[str]):
        self.dockerfile = dockerfile
        self.api_mode = api_mode

        add_extension(Span, "event")

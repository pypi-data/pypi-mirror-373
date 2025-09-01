# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Optional

from spacy.language import Language
from spacy.tokens import Span

from monapipe.pipeline.methods import add_extension


class SpaceTagger:
    """Component super class `SpaceTagger`."""

    assigns = {
        "doc.spans": "doc.spans['space']",
        "span._.space_type": "space_span._.space_type",
    }

    def __init__(self, nlp: Language, with_metaphors: bool, dockerfile: Optional[str], api_mode: Optional[str]):
        self.with_metaphors = with_metaphors
        self.dockerfile = dockerfile
        self.api_mode = api_mode

        add_extension(Span, "space_type")

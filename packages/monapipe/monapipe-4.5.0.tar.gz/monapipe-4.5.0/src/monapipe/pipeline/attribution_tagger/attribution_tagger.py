# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Span

from monapipe.pipeline.methods import add_extension


class AttributionTagger:
    """Component super class `AttributionTagger`."""

    assigns = {"span._.attribution": "clause._.attribution"}

    def __init__(self, nlp: Language, dockerfile: str, api_mode: str):
        self.dockerfile = dockerfile
        self.api_mode = api_mode

        add_extension(Span, "attribution")

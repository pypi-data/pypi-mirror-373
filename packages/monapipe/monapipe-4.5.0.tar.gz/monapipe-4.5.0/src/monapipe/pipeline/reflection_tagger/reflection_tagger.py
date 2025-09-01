# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Optional

from spacy.language import Language
from spacy.tokens import Span

from monapipe.pipeline.methods import add_extension


class ReflectionTagger:
    """Component super class `ReflectionTagger`."""

    assigns = {"doc.spans": "doc.spans['rp']", "span._.rp": "rp_span._.rp"}

    def __init__(
        self,
        nlp: Language,
        label_condition: str,
        dockerfile: Optional[str],
        api_mode: Optional[str],
    ):
        self.label_condition = label_condition
        self.dockerfile = dockerfile
        self.api_mode = api_mode

        add_extension(Span, "rp", {})

# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Span

from monapipe.pipeline.methods import add_extension


class TimeTagger:
    """Component super class `TimeTagger`."""

    assigns = {
        "doc.spans": "doc.spans['time']",
        "span._.time_norm": "time_span._.time_norm",
        "span._.time_type": "time_span._.time_type",
    }

    def __init__(self, nlp: Language):
        add_extension(Span, "time_norm")
        add_extension(Span, "time_type")

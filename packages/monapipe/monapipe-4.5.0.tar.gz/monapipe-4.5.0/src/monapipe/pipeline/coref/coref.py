# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Doc, Span, Token

from monapipe.pipeline.methods import add_extension


class Coref:
    """Component super class `Coref`."""

    assigns = {
        "doc._.coref_clusters",
        "doc._.coref_resolved",
        "doc._.coref_scores",
        "doc._.has_coref",
        "span._.coref_cluster",
        "span._.coref_scores",
        "span._.is_coref",
        "token._.coref_clusters",
        "token._.in_coref",
    }

    def __init__(self, nlp: Language):
        add_extension(Doc, "coref_clusters", [])
        add_extension(Doc, "coref_resolved")
        add_extension(Doc, "coref_scores", {})
        add_extension(Doc, "has_coref", False)
        add_extension(Span, "coref_cluster")
        add_extension(Span, "coref_scores", {})
        add_extension(Span, "is_coref", False)
        add_extension(Token, "coref_clusters", [])
        add_extension(Token, "in_coref", False)

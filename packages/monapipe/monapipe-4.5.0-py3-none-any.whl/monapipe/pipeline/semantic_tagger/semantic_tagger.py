# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Span, Token

from monapipe.pipeline.methods import add_extension


class SemanticTagger:
    """Component super class `SemanticTagger`."""

    assigns = {
        "span._.verb_synset_id": "clause._.verb_synset_id",
        "token._.synset_id": "token._.synset_id",
    }

    def __init__(self, nlp: Language):
        add_extension(Span, "verb_synset_id")
        add_extension(Token, "synset_id")

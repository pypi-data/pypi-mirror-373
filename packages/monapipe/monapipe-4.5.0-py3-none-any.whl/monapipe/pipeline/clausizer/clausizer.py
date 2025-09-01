# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import List

from spacy.language import Language
from spacy.tokens import Doc, Span, Token

from monapipe.pipeline.methods import add_extension


class Clausizer:
    """Component super class `Clausizer`."""

    assigns = {
        "doc._.clauses": "doc._.clauses",
        "span._.clauses": "sent._.clauses",
        "span._.prec_punct": "clause._.prec_punct",
        "span._.succ_punct": "clause._.succ_punct",
        "span._.tokens": "clause._.tokens",
        "token._.clause": "token._.clause",
    }

    def __init__(
        self,
        nlp: Language,
        dep_labels: List[str],
        conj_rule_labels: List[str],
        xcomp_rule_labels: List[str],
        handle_semi_modals: bool,
        include_ws: bool,
    ):
        self.dep_labels = dep_labels
        self.conj_rule_labels = conj_rule_labels
        self.xcomp_rule_labels = xcomp_rule_labels
        self.handle_semi_modals = handle_semi_modals
        self.include_ws = include_ws

        add_extension(Doc, "clauses", [])
        add_extension(Span, "clauses")
        add_extension(Span, "tokens")
        add_extension(Span, "prec_punct")
        add_extension(Span, "succ_punct")
        add_extension(Token, "clause")

# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import List

from spacy.language import Language
from spacy.tokens import MorphAnalysis, Span

from monapipe.pipeline.methods import add_extension


class VerbAnalyzer:
    """Component super class `VerbAnalyzer`."""

    assigns = {
        "span._.form": "clause._.form",
        "span._.form_main": "clause._.form_main",
        "span._.form_modals": "clause._.form_modals",
        "span._.form_verbs": "clause._.form_verbs",
    }

    def __init__(
        self,
        nlp: Language,
        ov: bool,
        conj_rule_labels: List[str],
        handle_semi_modals: bool,
        handle_particles: bool,
        handle_substitute_infinitives: bool,
        handle_local_verb_movement: bool,
    ):
        self.ov = ov
        self.conj_rule_labels = conj_rule_labels
        self.handle_semi_modals = handle_semi_modals
        self.handle_particles = handle_particles
        self.handle_substitute_infinitives = handle_substitute_infinitives
        self.handle_local_verb_movement = handle_local_verb_movement

        add_extension(Span, "form", MorphAnalysis(nlp.vocab, {}))
        add_extension(Span, "form_main", None)
        add_extension(Span, "form_modals", [])
        add_extension(Span, "form_verbs", [])

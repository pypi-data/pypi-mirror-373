# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Doc

from monapipe.pipeline.methods import add_extension


class Slicer:
    """Component super class `Slicer`."""

    assigns = ["doc.text", "doc._.fulltext"]

    def __init__(self, nlp: Language, max_units: int, units: str, complete_sentences: bool):
        self.max_units = max_units
        self.units = units
        self.complete_sentences = complete_sentences

        add_extension(Doc, "fulltext")

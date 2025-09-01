# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Optional

from spacy.language import Language
from spacy.tokens import Doc, Token

from monapipe.pipeline.methods import add_extension


class AnnotationReader:
    """Component super class `AnnotationReader`."""

    assigns = ["doc._.annotations", "token._.annotations"]

    def __init__(self, nlp: Language, corpus_path: Optional[str]):
        self.corpus_path = corpus_path

        add_extension(Token, "annotations", {})
        add_extension(Doc, "annotations", {})

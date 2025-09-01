# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language
from spacy.tokens import Doc, Token

from monapipe.pipeline.methods import add_extension


class Normalizer:
    """Component super class `Normalizer`."""

    assigns = [
        "doc.text",
        "doc.text_with_ws",
        "doc._.text",
        "doc._.text_with_ws",
        "token.idx",
        "token.text",
        "token.text_with_ws",
        "token._.idx",
        "token._.text",
        "token._.text_with_ws",
        "token._.whitespace_",
    ]

    def __init__(self, nlp: Language, remove_spaces: bool):
        self.remove_spaces = remove_spaces

        add_extension(Doc, "text")
        add_extension(Doc, "text_with_ws")
        add_extension(Token, "idx")
        add_extension(Token, "text")
        add_extension(Token, "text_with_ws")
        add_extension(Token, "whitespace_")

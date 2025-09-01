# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any

from spacy.language import Language
from spacy.tokens import Doc

from monapipe.pipeline.normalizer.normalizer import Normalizer


@Language.factory(
    "identity_normalizer",
    assigns=Normalizer.assigns,
    default_config={"remove_spaces": False},
)
def identity_normalizer(nlp: Language, name: str, remove_spaces: bool) -> Any:
    """Spacy component implementation.
        Normalises each token with its actual form.

    Args:
        nlp: Spacy object.
        name: Component name.
        remove_spaces: Specifies whether SPACE tokens should be removed.

    Returns:
        `IdentityNormalizer`.

    """
    return IdentityNormalizer(nlp, remove_spaces)


class IdentityNormalizer(Normalizer):
    """The class `IdentityNormalizer`."""

    def __init__(self, nlp: Language, remove_spaces: bool):
        self.remove_spaces = remove_spaces

        super().__init__(nlp, remove_spaces)

    def __call__(self, doc: Doc) -> Doc:
        # token.text cannot be overwritten, so we create a new document
        tokens = []
        spaces = []
        for token in doc:
            if not (self.remove_spaces and token.is_space):
                tokens.append(token.text)
                spaces.append(token.whitespace_ != "")
            elif len(spaces) > 0:
                spaces[-1] = True
        new_doc = Doc(doc.vocab, tokens, spaces)

        # copy some document-level information from the original document
        new_doc._.text = doc.text
        new_doc._.text_with_ws = doc.text_with_ws

        # copy some token-level information from the original tokens
        offset = 0
        for i, token in enumerate(doc):
            if not (self.remove_spaces and token.is_space):
                new_doc[i - offset]._.idx = doc[i].idx
                new_doc[i - offset]._.text = doc[i].text
                new_doc[i - offset]._.text_with_ws = doc[i].text_with_ws
                new_doc[i - offset]._.whitespace_ = doc[i].whitespace_
            else:
                offset += 1

        return new_doc

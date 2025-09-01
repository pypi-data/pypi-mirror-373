# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from spacy.language import Language


class EntityLinker:
    """Component super class `EntityLinker`."""

    assigns = {}

    def __init__(self, nlp: Language, dockerfile: str, api_mode: str) -> None:
        self.dockerfile = dockerfile
        self.api_mode = api_mode

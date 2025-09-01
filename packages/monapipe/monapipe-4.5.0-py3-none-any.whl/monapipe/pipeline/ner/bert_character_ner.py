# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys
from typing import Any, List, Tuple

import requests
from spacy.language import Language
from spacy.tokens import Doc

from monapipe.config import PORTS
from monapipe.docker import provide_docker_container
from monapipe.pipeline.ner.methods import create_ents_from_token_bio
from monapipe.pipeline.ner.ner import EntityRecognizer

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "bert_character_ner_api")


@Language.factory(
    "bert_character_ner",
    assigns=EntityRecognizer.assigns,
    default_config={"set_ents_mode": "reset", "dockerfile": "Dockerfile", "api_mode": "localhost"},
)
def bert_character_ner(
    nlp: Language, name: str, set_ents_mode: str, dockerfile: str, api_mode: str
) -> Any:
    """Spacy component implementation.

    Args:
        nlp: Spacy object.
        name: Component name.
        set_ents_mode: Specifies how the new entities should be added w.r.t. existing entities in `doc.ents`.
            - "r" or "reset": The new entities overwrite the existing entities.
            - "s" or "substitute": The new entities substitute existing entities of the same label(s). Existing entities with other labels remain unchanged.
            - "u" or "unify": The new entities are unified with the existing entities.
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `BertCharacterNer`.
    """
    return BertCharacterNer(nlp, set_ents_mode, dockerfile, api_mode)


class BertCharacterNer(EntityRecognizer):
    """The class `BertCharacterNer`."""

    def __init__(self, nlp: Language, set_ents_mode: str, dockerfile: str, api_mode: str):
        super().__init__(nlp, set_ents_mode, dockerfile, api_mode)

        self.container_port = PORTS["bert_character_ner"]["container_port"]
        self.host_port = PORTS["bert_character_ner"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
            )

    def __call__(self, doc: Doc) -> Doc:
        sentences = self.split_doc(doc)

        # define API endpoint
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/bert_character_ner_api/"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/bert_character_ner_api/"
        else:
            sys.exit(
                """
                     Please choose provided API mode `localhost` (for local usage)
                     or `service` (for gitlab-ci service)."""
            )
        response = requests.post(url, json=sentences, timeout=10000)

        if response.status_code == 200:
            # Response successful, extract JSON data to Python dictionary
            data = response.json()
        else:
            # Error in the request
            error_msg = f"Error message: {response.status_code}"
            sys.exit(error_msg)

        token_bio = {int(k): v for k, v in data.items()}
        create_ents_from_token_bio(doc, token_bio, self.set_ents_mode)

        return doc

    @staticmethod
    def split_doc(doc: Doc) -> List[List[Tuple[str, int]]]:
        """Splits the content of sentences and tokens.
            Tokens are globally enumerated

        Args:
            doc: Doc to split

        Returns:
            List containing a sublist for each sentence; each sentence contains tuples of words and their global_ids.

        """
        word_idx = 0
        splitted = []
        for s in doc.sents:
            sent = []
            for t in s:
                sent.append((t.text, word_idx))
                word_idx += 1
            splitted.append(sent)
        return splitted

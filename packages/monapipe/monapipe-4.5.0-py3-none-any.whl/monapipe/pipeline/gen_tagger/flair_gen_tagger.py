# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys
from typing import Any

import requests
from spacy.language import Language
from spacy.tokens import Doc

from monapipe.config import PORTS
from monapipe.docker import provide_docker_container
from monapipe.pipeline.gen_tagger.gen_tagger import GenTagger
from monapipe.pipeline.methods import requires, update_token_span_groups
from monapipe.pipeline.reflection_tagger.methods import create_passages_from_clause_tags

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "flair_gen_tagger_api")


@Language.factory(
    "flair_gen_tagger",
    assigns=GenTagger.assigns,
    default_config={
        "label_condition": "multi",
        "dockerfile": "Dockerfile",
        "api_mode": "localhost",
    },
)
def flair_gen_tagger(
    nlp: Language, name: str, label_condition: str, dockerfile: str, api_mode: str
) -> Any:
    """Spacy component implementation.
        Add generalising passages to the document.
        Uses the code and the multi-class model from here:
        https://gitlab.gwdg.de/tillmann.doenicke/thesis

    Args:
        nlp: Spacy object.
        name: Component name.
        label_condition: Label condition ("multi" or "binary").
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `FlairGenTagger`.

    """
    return FlairGenTagger(nlp, label_condition, dockerfile, api_mode)


class FlairGenTagger(GenTagger):
    """The class `FlairGenTagger`."""

    def __init__(self, nlp: Language, label_condition: str, dockerfile: str, api_mode: str):
        requires(self, nlp, ["clausizer"])

        if label_condition not in ["binary", "multi"]:
            raise ValueError('Label condition must be "binary" or "multi".')

        super().__init__(nlp, label_condition, dockerfile, api_mode)

        self.container_port = PORTS["flair_gen_tagger"]["container_port"]
        self.host_port = PORTS["flair_gen_tagger"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
                debug_mode=False,
            )

    def __call__(self, doc: Doc) -> Doc:

        # define API endpoint
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/flair_gen_tagger_api"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/flair_gen_tagger_api"
        else:
            sys.exit(
                """
                    Please choose provided API mode `localhost` (for local usage)
                    or `service` (for gitlab-ci service)."""
            )

        all_clause_labels = {}

        chunks = []
        chunk = []
        for sent in doc.sents:
            tokens = list(sent)
            if len(chunk) + len(tokens) <= 100 or len(chunk) == 0:
                chunk.extend(tokens)
            else:
                chunks.append(chunk)
                chunk = tokens
        if len(chunk) > 0:
            chunks.append(chunk)
        for chunk in chunks:
            chunk = [
                {
                    "text": token.text,
                    "clause": (
                        None if token._.clause is None else doc._.clauses.index(token._.clause)
                    ),
                    "is_space": token.is_space,
                }
                for token in chunk
            ]

            response = requests.post(
                url,
                json=chunk,
                timeout=10000,
            )

            if response.status_code == 200:
                # Response successful, extract JSON data to Python dictionary
                data = response.json()
                clause_labels = data["flair_gen_tagger"]

            else:
                # Error in the request
                error_msg = f"Error message: {response.status_code}"
                sys.exit(error_msg)

            clause_labels = {
                doc._.clauses[int(clause)]: clause_labels[clause] for clause in clause_labels
            }

            for clause in clause_labels:
                all_clause_labels[clause] = clause_labels[clause]

        if self.label_condition == "binary":
            for clause in all_clause_labels:
                if len(all_clause_labels[clause]) > 0:
                    all_clause_labels[clause].clear()
                    all_clause_labels[clause].add("GI")

        labels = []
        for clause in doc._.clauses:
            try:
                labels.append(all_clause_labels[clause])
            except KeyError:
                labels.append(set())

        create_passages_from_clause_tags(doc, "gi", labels)

        update_token_span_groups(doc, ["gi"])

        return doc

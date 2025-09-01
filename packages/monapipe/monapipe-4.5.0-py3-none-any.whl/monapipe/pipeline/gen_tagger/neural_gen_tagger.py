# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
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

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "neural_gen_tagger_api")


@Language.factory(
    "neural_gen_tagger",
    assigns=GenTagger.assigns,
    default_config={
        "label_condition": "multi",
        "dockerfile": "Dockerfile",
        "api_mode": "localhost",
    },
)
def neural_gen_tagger(
    nlp: Language, name: str, label_condition: str, dockerfile: str, api_mode: str
) -> Any:
    """Spacy component implementation.
        Add generalising passages to the document.
        Uses the code and models from here:
        https://github.com/tschomacker/generalizing-passages-identification-bert

    Args:
        nlp: Spacy object.
        name: Component name.
        label_condition: Label condition ("multi" or "binary").
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `NeuralGenTagger`.

    """
    return NeuralGenTagger(nlp, label_condition, dockerfile, api_mode)


class NeuralGenTagger(GenTagger):
    """The class `NeuralGenTagger`."""

    def __init__(self, nlp: Language, label_condition: str, dockerfile: str, api_mode: str):
        requires(self, nlp, ["clausizer"])

        if label_condition not in ["binary", "multi"]:
            raise ValueError('Label condition must be "binary" or "multi".')

        super().__init__(nlp, label_condition, dockerfile, api_mode)

        self.container_port = PORTS["neural_gen_tagger"]["container_port"]
        self.host_port = PORTS["neural_gen_tagger"]["host_port"]

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
            url = f"http://localhost:{self.host_port}/neural_gen_tagger_api"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/neural_gen_tagger_api"
        else:
            sys.exit(
                """
                    Please choose provided API mode `localhost` (for local usage)
                    or `service` (for gitlab-ci service)."""
            )

        tag_names = (
            ["NONE", "ALL", "BARE", "DIV", "EXIST", "MEIST", "NEG"]
            if self.label_condition == "multi"
            else ["GI"]
        )

        clause_tags = []
        sents = [None] + list(doc.sents) + [None]
        for i in range(1, len(sents) - 1):
            context_tokens = []
            try:
                context_tokens.extend(list(sents[i - 1]))
            except TypeError:
                pass  # first sentence
            context_tokens.extend(list(sents[i]))
            try:
                context_tokens.extend(list(sents[i + 1]))
            except TypeError:
                pass  # last sentence
            context_tokens = [token for token in context_tokens if not token.is_space]

            for clause in sents[i]._.clauses:
                clause_open = False
                clause_text_embed_in_context = ""
                for token in context_tokens:
                    if token._.clause is not None:
                        # token is part of the current clause
                        if token._.clause == clause:
                            if not clause_open:
                                # start the clause mark up
                                clause_text_embed_in_context += "<b>"
                                clause_open = True
                        # token is NOT part of the current clause
                        else:
                            if clause_open:
                                # close the clause mark up
                                clause_text_embed_in_context += "</b>"
                                clause_open = False
                        clause_text_embed_in_context += " " + token.text
                    # punctation
                    else:
                        clause_text_embed_in_context += token.text
                    # closing the mark up, in case the passage conists of a single clause
                if clause_open:
                    clause_text_embed_in_context += "</b>"

                response = requests.get(
                    url,
                    params={
                        "clause_text_embed_in_context": clause_text_embed_in_context,
                        "label_condition": self.label_condition,
                    },
                    timeout=10000,
                )

                if response.status_code == 200:
                    # Response successful, extract JSON data to Python dictionary
                    data = response.json()
                    prediction = data["neural_gen_tagger"]

                else:
                    # Error in the request
                    error_msg = f"Error message: {response.status_code}"
                    sys.exit(error_msg)

                clause_tags.append(
                    set(
                        [
                            tag_name
                            for tag_i, tag_name in enumerate(tag_names)
                            if bool(prediction[tag_i]) and tag_name != "NONE"
                        ]
                    )
                )

        create_passages_from_clause_tags(doc, "gi", clause_tags)

        update_token_span_groups(doc, ["gi"])

        return doc

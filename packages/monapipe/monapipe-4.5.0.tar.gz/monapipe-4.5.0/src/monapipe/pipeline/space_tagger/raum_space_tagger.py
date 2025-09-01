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
from monapipe.pipeline.methods import get_alignments, update_token_span_groups
from monapipe.pipeline.space_tagger.space_tagger import SpaceTagger

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "raum_space_tagger_api")


@Language.factory(
    "raum_space_tagger",
    assigns=SpaceTagger.assigns,
    default_config={"with_metaphors": False, "dockerfile": "Dockerfile", "api_mode": "localhost"},
)
def raum_space_tagger(nlp: Language, name: str, with_metaphors: bool, dockerfile: str, api_mode: str) -> Any:
    """Spacy component implementation.
        Adds space mentions to the document.
        Uses the models from here: https://github.com/M-K-Schumacher/Raum-Classifier/tree/v1.0.0

    Args:
        nlp: Spacy object.
        name: Component name.
        with_metaphors: Whether to consider spaces in metaphors.

    Returns:
        `RaumSpaceTagger`.

    """
    return RaumSpaceTagger(nlp, with_metaphors, dockerfile, api_mode)


class RaumSpaceTagger(SpaceTagger):
    """The class `RaumSpaceTagger`."""

    def __init__(self, nlp: Language, with_metaphors: bool, dockerfile: str, api_mode: str):
        super().__init__(nlp, with_metaphors, dockerfile, api_mode)

        self.container_port = PORTS["raum_space_tagger"]["container_port"]
        self.host_port = PORTS["raum_space_tagger"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
            )

    def __call__(self, doc: Doc) -> Doc:
        doc.spans["space"] = []
        data = {"text": doc.text, "with_metaphors": self.with_metaphors}

        # define API endpoint
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/raum_space_tagger_api/"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/raum_space_tagger_api/"
        else:
            sys.exit(
                """
                     Please choose provided API mode `localhost` (for local usage)
                     or `service` (for gitlab-ci service)."""
            )
        response = requests.post(url, json=data, timeout=10000)

        if response.status_code == 200:
            # Response successful, extract JSON data to Python dictionary
            data = response.json()
        else:
            # Error in the request
            error_msg = f"Error message: {response.status_code}"
            sys.exit(error_msg)

        _, corenlp2doc = get_alignments(doc, data["corenlp_tokens"])
        for start_end_label_tuple in data["start_end_label_tuple"]:
            start, end, label = start_end_label_tuple
            start = corenlp2doc[start][0]
            end = corenlp2doc[end][-1]
            if start < end:
                span = doc[start:end]
                span._.space_type = label
                doc.spans["space"].append(span)

        update_token_span_groups(doc, ["space"])

        return doc

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
from monapipe.pipeline.event_tagger.event_tagger import EventTagger
from monapipe.pipeline.methods import requires

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "neural_event_tagger_api")


@Language.factory(
    "neural_event_tagger",
    assigns=EventTagger.assigns,
    default_config={"dockerfile": "Dockerfile", "api_mode": "localhost"},
)
def neural_event_tagger(nlp: Language, name: str, dockerfile: str, api_mode: str) -> Any:
    """Spacy component implementation.
        Integration of event classification from EvENT project.
        Uses the code and models from here:
        https://github.com/uhh-lt/event-classification

    Args:
        nlp: Spacy object.
        name: Component name.
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `NeuralEventTagger`.

    """
    return NeuralEventTagger(nlp, dockerfile, api_mode)


class NeuralEventTagger(EventTagger):
    """The class `NeuralEventTagger`."""

    def __init__(self, nlp: Language, dockerfile: str, api_mode: str):
        requires(self, nlp, ["clausizer"])

        super().__init__(nlp, dockerfile, api_mode)

        self.container_port = PORTS["neural_event_tagger"]["container_port"]
        self.host_port = PORTS["neural_event_tagger"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
            )

    def __call__(self, doc: Doc) -> Doc:

        annotations = []
        annotation_start_to_clause = {}
        for clause in doc._.clauses:
            annotation = {
                "start": clause[0].idx,
                "end": clause[-1].idx,
                "spans": [(clause[0].idx, clause[-1].idx)],
                "predicted": None,
            }
            annotations.append(annotation)
            annotation_start_to_clause[clause[0].idx] = clause
        data = {"text": doc.text, "annotations": annotations, "title": None}

        # define API endpoint
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/neural_event_tagger_api/"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/neural_event_tagger_api/"
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

        for annotation in data["annotations"]:
            annotation_start_to_clause[annotation["start"]]._.event = annotation[
                "additional_predictions"
            ]

        return doc

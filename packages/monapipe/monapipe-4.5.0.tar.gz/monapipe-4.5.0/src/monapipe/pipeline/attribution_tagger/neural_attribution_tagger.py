# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import json
import os
import sys
from typing import Any, Dict, List, Optional, Union

import requests
from spacy.language import Language
from spacy.tokens import Doc

from monapipe.config import PORTS
from monapipe.docker import provide_docker_container
from monapipe.pipeline.attribution_tagger.attribution_tagger import AttributionTagger
from monapipe.pipeline.methods import requires

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "neural_attribution_tagger_api")


@Language.factory(
    "neural_attribution_tagger",
    assigns=AttributionTagger.assigns,
    default_config={"dockerfile": "Dockerfile", "api_mode": "localhost"},
)
def neural_attribution_tagger(nlp: Language, name: str, dockerfile: str, api_mode: str) -> Any:
    """Spacy component implementation.
        Add speaker attribution to each clause.
        Uses the model from Dönicke et al. (2022):
        "Modelling Speaker Attribution in Narrative Texts With Biased and Bias-Adjustable Neural Networks".
        (https://gitlab.gwdg.de/mona/neural-attribution)

    Args:
        nlp: Spacy object.
        name: Component name.
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `NeuralAttributionTagger`.

    """
    return NeuralAttributionTagger(nlp, dockerfile, api_mode)


class NeuralAttributionTagger(AttributionTagger):
    """The class `NeuralAttributionTagger`."""

    def __init__(self, nlp: Language, dockerfile: str, api_mode: str):
        requires(self, nlp, ["clausizer"])

        super().__init__(nlp, dockerfile, api_mode)

        self.container_port = PORTS["neural_attribution_tagger"]["container_port"]
        self.host_port = PORTS["neural_attribution_tagger"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
            )

    def __call__(self, doc: Doc) -> Doc:
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/neural_attribution_tagger_api/"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/neural_attribution_tagger_api/"
        else:
            sys.exit(
                """
                     Please choose provided API mode `localhost` (for local usage)
                     or `service` (for gitlab-ci service)."""
            )
        response = requests.post(
            url,
            json=self._prepare_sents_for_api(doc),
            timeout=10000,
        )

        if response.status_code == 200:
            # Response successful, extract JSON data
            data = response.json()
        else:
            # Error in the request
            error_msg = f"Error message: {response.status_code}"
            sys.exit(error_msg)

        # assign labels to each clause
        for sent in doc.sents:
            for clause in sent._.clauses:
                clause._.attribution = set(data["neural_attribution_tagger"].pop(0))

        return doc

    def _prepare_sents_for_api(self, doc: Doc) -> List[List[Dict[str, Union[str, Optional[int]]]]]:
        """Convert `doc.sents` to a nested list of strings and integers.

        Args:
            doc: The document.

        Returns:
            The sentences of the document as list of lists of tokens.
                Each token is a dictionary with two keys:
                    - "text": The token's text.
                    - "clause": The token's clause index (within the sentence) or `None`.

        """
        sentences = []
        for sent in doc.sents:
            sentence = []
            for token in sent:
                if not token.is_space:
                    word = {}
                    word["text"] = token.text
                    word["clause"] = None
                    if token._.clause is not None:
                        word["clause"] = sent._.clauses.index(token._.clause)
                    sentence.append(word)
            sentences.append(sentence)
        return sentences

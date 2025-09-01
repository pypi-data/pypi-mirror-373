# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys
from string import punctuation
from typing import Any, Dict, List, Optional, Union

import requests
from spacy.language import Language
from spacy.tokens import Doc, Span

from monapipe.config import PORTS
from monapipe.docker import provide_docker_container
from monapipe.pipeline.entity_linker.entity_linker import EntityLinker
from monapipe.pipeline.methods import add_extension

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "embedding_entity_linker_api")


@Language.factory(
    "embedding_entity_linker",
    assigns=EntityLinker.assigns,
    default_config={
        "dockerfile": "Dockerfile",
        "api_mode": "localhost"
    },
)
def embedding_entity_linker(
    nlp: Language,
    name: str,
    dockerfile: str = None,
    api_mode: str = None,
) -> Any:
    """Spacy component implementation.
       Finds and ranks GND ID candidates for named entities in the doc.
    
    Args:
        nlp: Spacy object.
        name: Component name.
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `EntityLinker`.
    """
    return EmbeddingEntityLinker(nlp, dockerfile, api_mode)


class EmbeddingEntityLinker(EntityLinker):
    """The class `EmbeddingEntityLinker`."""

    def __init__(self, nlp: Language, dockerfile: str, api_mode: str):

        super().__init__(nlp, dockerfile, api_mode)

        self.container_port = PORTS["embedding_entity_linker"]["container_port"]
        self.host_port = PORTS["embedding_entity_linker"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
            )

        # Span extension for entity candidates
        add_extension(Span, "candidates", [])

    def __call__(self, doc: Doc) -> Doc:

        # Iterate over every named entity present in the Doc
        for entity in doc.ents:

            # from the entity name in the text, generate variants to hopefully find the fitting GND candidates
            input_name_variants = self._generate_name_variants(entity.text)

            # get the context from which the embedding will be generated (add sentence terms again to give them higher weight)
            input_context = [e.text for e in doc.ents] + [e.text for e in entity.sent.ents]

            # call the API to calculate embedding and string similarities
            candidates_with_similarities = self._get_embedding_similarities_api(input_context, input_name_variants)

            entity._.candidates = candidates_with_similarities

        return doc

    def _generate_name_variants(self, base_name: str) -> list:
        """
        For a given base name, generate a list of several variants, including the original one.

        Args:
            base_name: The base name.

        Returns:
            List of name variants
        """
        variants = [base_name]

        # include a variation that combines all different variations
        variant_all = base_name

        char_replacements = {
            'ä': 'ae',
            'Ä': 'Ae',
            'ö': 'oe',
            'Ö': 'Oe',
            'ü': 'ue',
            'Ü': 'Ue',
            'ß': 'ss',
        }

        # char replacements
        for variant in [base_name, variant_all]:
            for replacement_target in char_replacements:
                variant = variant.replace(replacement_target, char_replacements[replacement_target])
            variants.append(variant)

        # remove leading and trailing punctuation
        for variant in [base_name, variant_all]:
            variant = variant.strip(punctuation)
            variants.append(variant)

        # Last part of the name only, hopefully coinciding with the last name
        for variant in [base_name, variant_all]:
            variant_split = variant.split(' ')
            if len(variant_split) > 1:
                variants.append(variant_split[-1])

        # filter out duplicates
        variants = list(set(variants))

        return variants


    def _get_embedding_similarities_api(self, input_context: list, input_name_variants: list) -> List[Dict[str, Union[str, Optional[float]]]]:
        """Get the candidates embedding similarities between the candidate embeddings and the embedding of the input context.

        Args:
            input_context: A list of token making up the input context.
            input_name_variants: A list of names of the input entity

        Returns:
            List of dictionaries with GND-ID and scores for embedding and string similarities (emb_similarity can be None if no candidate embedding existed).

        """
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/embedding_entity_linker_api/"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/embedding_entity_linker_api/"
        else:
            sys.exit(
                """
                     Please choose provided API mode `localhost` (for local usage)
                     or `service` (for gitlab-ci service)."""
            )
        response = requests.post(
            url, json={"input_context": input_context, "input_name_variants": input_name_variants}, timeout=10000
        )

        if response.status_code == 200:
            # Response successful, extract JSON data
            data = response.json()
        else:
            # Error in the request
            error_msg = f"Error message: {response.status_code}"
            sys.exit(error_msg)

        return data

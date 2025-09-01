# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys
from typing import Any

import requests
from spacy.language import Language
from spacy.tokens import Doc, Span

from monapipe.config import PORTS
from monapipe.docker import provide_docker_container
from monapipe.pipeline.methods import requires, update_token_span_groups
from monapipe.pipeline.speech_tagger.methods import (
    create_speech_segments_from_token_tags,
)
from monapipe.pipeline.speech_tagger.speech_tagger import SpeechTagger

DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "flair_speech_tagger_api")


@Language.factory(
    "flair_speech_tagger",
    assigns=SpeechTagger.assigns,
    default_config={"sentence_level": False, "dockerfile": "Dockerfile", "api_mode": "localhost"},
)
def flair_speech_tagger(
    nlp: Language, name: str, sentence_level: bool, dockerfile: str, api_mode: str
) -> Any:
    """Spacy component implementation.
        Tags tokens and clauses with speech tags.
        Wrapper for the "Redewiedergabe" taggers from https://github.com/redewiedergabe/tagger.

    Args:
        nlp: Spacy object.
        name: Component name.
        sentence_level: If True, the taggers take each sentence separately as input;
            if False, the taggers take chunks of up to 100 tokens as input.
        dockerfile: The Dockerfile to build the API container.
        api_mode: API source, localhost by docker ("localhost") or service api for gitlab-ci ("service").
            Online API will be implemented in the future.

    Returns:
        `FlairSpeechTagger`.

    """
    return FlairSpeechTagger(nlp, sentence_level, dockerfile, api_mode)


class FlairSpeechTagger(SpeechTagger):
    """The class `FlairSpeechTagger`."""

    def __init__(self, nlp: Language, sentence_level: bool, dockerfile: str, api_mode: str):
        requires(self, nlp, ["parser"])

        super().__init__(nlp, sentence_level, dockerfile, api_mode)

        self.container_port = PORTS["flair_speech_tagger"]["container_port"]
        self.host_port = PORTS["flair_speech_tagger"]["host_port"]

        if self.api_mode == "localhost":
            provide_docker_container(
                dockerfile_dir=DOCKERFILE_DIR,
                dockerfile=self.dockerfile,
                container_port=self.container_port,
                host_port=self.host_port,
            )

    def __call__(self, doc: Doc) -> Doc:
        for token in doc:
            token._.speech = {}

        if self.sentence_level:
            for sent in doc.sents:
                text = " ".join([token.text for token in sent if not token.is_space])
                self._add_speech_tags_to_tokens_api(sent, text, "indirect")
                self._add_speech_tags_to_tokens_api(sent, text, "freeIndirect")
                self._add_speech_tags_to_tokens_api(sent, text, "direct")
                self._add_speech_tags_to_tokens_api(sent, text, "reported")
        else:
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
                text = " ".join([token.text for token in chunk if not token.is_space])
                self._add_speech_tags_to_tokens_api(chunk, text, "indirect")
                self._add_speech_tags_to_tokens_api(chunk, text, "freeIndirect")
                self._add_speech_tags_to_tokens_api(chunk, text, "direct")
                self._add_speech_tags_to_tokens_api(chunk, text, "reported")

        create_speech_segments_from_token_tags(
            doc, ["indirect", "freeIndirect", "direct", "reported"]
        )

        update_token_span_groups(doc, ["speech"])

        return doc

    def _add_speech_tags_to_tokens_api(self, sent: Span, txt: str, speech_type: str):
        """Add speech tags to tokens in a sentence.

        Args:
            sent: The sentence in spacy format.
            txt: The sentence string format.
            speech_type: The speech type to tag.
        """
        if self.api_mode == "localhost":
            url = f"http://localhost:{self.host_port}/flair_speech_tagger_api/"
        elif self.api_mode == "service":
            url = f"http://service:{self.container_port}/flair_speech_tagger_api/"
        else:
            sys.exit(
                """
                     Please choose provided API mode `localhost` (for local usage)
                     or `service` (for gitlab-ci service)."""
            )
        response = requests.get(
            url, params={"sentence": txt, "speech_type": speech_type}, timeout=10000
        )

        if response.status_code == 200:
            # Response successful, extract JSON data
            data = response.json()
        else:
            # Error in the request
            error_msg = f"Error message: {response.status_code}"
            sys.exit(error_msg)

        # if nothing is tagged in sentence, API returns empty list
        if len(data["flair_speech_tagger"]) > 0:
            offset = 0
            for i, token in enumerate(sent):
                try:
                    if token.is_space:
                        offset += 1
                    else:
                        if data["flair_speech_tagger"][i - offset]["score"] is not None:
                            token._.speech[speech_type] = data["flair_speech_tagger"][i - offset][
                                "score"
                            ]
                except IndexError as e:
                    print(f"Error message: {url}\n{repr(e)}")

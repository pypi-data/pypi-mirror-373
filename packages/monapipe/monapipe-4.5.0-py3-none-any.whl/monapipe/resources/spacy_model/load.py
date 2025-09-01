# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os

import spacy_download
from spacy.language import Language

from monapipe.config import SETTINGS
from monapipe.resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Language:
    """Loading method of the `spacy_model` resource.

    Returns:
        The built-in German spacy model.

    """
    nlp = spacy_download.load_spacy("de_core_news_lg")
    nlp.max_length = SETTINGS["spacy_max_length"]
    return nlp

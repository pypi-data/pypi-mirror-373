# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os

import spacy
from spacy.language import Language

from monapipe.config import SETTINGS
from monapipe.resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Language:
    """Loading method of the `parsing` resource.

    Returns:
        A German UD spacy model.

    """
    name = "de_ud_md"
    version = "-0.0.0"
    model_path = os.path.join(RESOURCE_HANDLER.data_path, name + version, name, name + version)
    nlp = spacy.load(model_path)
    nlp.max_length = SETTINGS["spacy_max_length"]
    return nlp

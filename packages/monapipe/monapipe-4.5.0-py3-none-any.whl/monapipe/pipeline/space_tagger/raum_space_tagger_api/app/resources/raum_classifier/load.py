# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
from typing import Dict

import stanza
from resource_handler import ResourceHandler
from stanza.server import CoreNLPClient

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Dict[str, CoreNLPClient]:
    """Loading method of the `raum_classifier` resource.

    Returns:
        A dictionary of stanza `CoreNLPClient` objects for the two Raum-Classifier models.

    """
    corenlp_version = "4.2.2"
    corenlp_path = os.path.join(RESOURCE_HANDLER.data_path, "corenlp", corenlp_version)
    if not os.path.exists(corenlp_path):
        stanza.install_corenlp(dir=corenlp_path, version=corenlp_version)

    clients = {}
    for metaphors in ["", "_ohneMetaphern"]:
        model_name = "Raum320000_18-21Jh" + metaphors + "_ner-model.ser.gz"
        with CoreNLPClient(
            be_quiet=True,
            classpath=os.path.join(corenlp_path, "*"),
            properties={
                "annotators": "tokenize,ner",
                "ner.model": os.path.join(RESOURCE_HANDLER.data_path, model_name),
                "tokenize.language": "de",
            },
        ) as client:
            clients[metaphors] = client
    return clients

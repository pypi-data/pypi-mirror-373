# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
from pathlib import Path

from torch import cuda

# Set the data directory to a custom location if the MONAPIPE_DATA environment variable is set
# Otherwise, use the default location
home = Path.home()
DATA_DIR = os.getenv("MONAPIPE_DATA")
if not DATA_DIR:
    DATA_DIR = os.path.join(home, ".monapipe_data")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

DATAVERSE = {
    "api_token": "",
    "doi_embedding_entity_linker": "doi:10.25625/SZ0IBE&version=1.0",
    "doi_event_classification": "doi:10.25625/0GUOMC&version=1.1",
    "doi_flair_gen_tagger_cv": "doi:10.25625/V7HTB8&version=2.1",
    "doi_generalizing_passages_identification_bert": "doi:10.25625/2PHXNC&version=1.1",
    "doi_heideltime": "doi:10.25625/SIPQEF&version=1.0",
    "doi_neural_attribution_tagger": "doi:10.25625/2D9CAV&version=1.0",
    "doi_open_multilingual_wordnet": "doi:10.25625/LE57DV&version=1.0",
    "doi_parsing": "doi:10.25625/S2LPJP&version=1.1",
    "doi_raum_classifier": "doi:10.25625/KILDMC&version=1.0",
    "doi_reflective_passages_identification_bert": "doi:10.25625/0HXWYG&version=1.1",
}

HUGGINGFACE_HUB = {
    "fiction-gbert-char-ner": {
        "pretrained_model_name_or_path": "LennartKeller/fiction-gbert-large-droc-np-ner",
        "revision": "a75cf9fe8be4e45856049c289a0317c82f68c50a",
    }
}

LOCAL_PATHS = {
    "germanet": os.path.join(os.path.dirname(__file__), "..", "..", "..", "germanet"),
    "data_path": DATA_DIR,
    "data_path_container": "/app/data",
}

SETTINGS = {
    "spacy_max_length": 12000000,
    "torch_device": ("cuda" if cuda.is_available() else "cpu"),
    "fasttext_model": "cc.de.300.bin",
    "gnd_embedding_file": "gnd_entity_embeddings.h5",
    "gnd_name_file": "gnd_names.csv"
}

# ports for the API services:
# - internal/container port
#   -> Always 80 (otherwise the `integration tests` in `.gitlab-ci.yml` won't work)
# - external/host port
#   -> Counted up from 16000
API_SERVICES = [
    "bert_character_ner",
    "embedding_entity_linker",
    "flair_gen_tagger",
    "flair_speech_tagger",
    "neural_attribution_tagger",
    "neural_event_tagger",
    "neural_gen_tagger",
    "neural_reflection_tagger",
    "raum_space_tagger",
]
PORTS = {
    name: {"container_port": 80, "host_port": 16000 + i} for i, name in enumerate(API_SERVICES)
}

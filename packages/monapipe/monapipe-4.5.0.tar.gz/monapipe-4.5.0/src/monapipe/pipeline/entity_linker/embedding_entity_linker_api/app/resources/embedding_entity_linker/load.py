# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import csv
import os
import re
from typing import Dict, List, Tuple

import fasttext
import h5py
from resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Tuple[fasttext.FastText._FastText, List[Tuple[str, List[str]]], Dict[str, List[float]]]:
    """Loading resources for the `embedding_entity_linker`.

    Returns:
        fasttext model
        List of tuples of GND Ids and a list of names
        Dict of GND entity embeddings, with GND-IDs as keys

    """
    # Load fasttext model
    fasttext_model = fasttext.load_model(os.path.join(RESOURCE_HANDLER.data_path, "cc.de.300.bin"))

    gnd_names = []
    with open(os.path.join(RESOURCE_HANDLER.data_path, "gnd_names.csv"), newline='') as csvreader:
        reader = csv.reader(csvreader, delimiter='\t')
        for row in reader:
            gnd_id = row.pop(0).replace('https://d-nb.info/gnd/','')
            row.pop(0)
            names = [re.sub(r' \([^\]]+\)', '', row[name]) for name in range(0, len(row))]
            gnd_names.append((gnd_id, names))

    gnd_embeddings = {}
    with h5py.File(os.path.join(RESOURCE_HANDLER.data_path, "gnd_entity_embeddings.h5"), 'r') as f:
        for key in f.keys():
            gnd_embeddings[key] = f[key][:]

    return fasttext_model, gnd_names, gnd_embeddings

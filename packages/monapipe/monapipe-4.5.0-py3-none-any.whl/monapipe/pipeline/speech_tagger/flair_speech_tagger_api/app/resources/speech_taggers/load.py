# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
from typing import Dict

import flair
import torch
from config import SETTINGS
from flair.models import SequenceTagger
from resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Dict[str, SequenceTagger]:
    """Loading method of the `speech_taggers` resource.
        Load pre-trained "Redewiedergabe" taggers.

    Returns:
        Dictionary mapping a speech type to the corresponding tagger.
            The speech types are: "indirect", "freeIndirect", "direct", "reported".

    """
    flair.cache_root = os.path.join(RESOURCE_HANDLER.data_path, "flair")
    flair.device = torch.device(SETTINGS["torch_device"])
    speech_taggers = {}
    speech_taggers["indirect"] = SequenceTagger.load("de-historic-indirect")
    speech_taggers["freeIndirect"] = SequenceTagger.load("de-historic-free-indirect")
    speech_taggers["direct"] = SequenceTagger.load("de-historic-direct")
    speech_taggers["reported"] = SequenceTagger.load("de-historic-reported")
    return speech_taggers

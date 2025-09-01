# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys

import flair
import flair.samplers
import torch
from config import SETTINGS
from flair.models import SequenceTagger
from resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> SequenceTagger:
    """Loading method of the `flair_gen_tagger_cv` resource.

    Returns:
        The multi-class model.

    """
    flair.device = torch.device(SETTINGS["torch_device"])
    sys.modules["imbalanced_sampler"] = flair.samplers
    return SequenceTagger.load(
        os.path.join(RESOURCE_HANDLER.data_path, "multi_100_mixed1_5", "final-model.pt")
    )

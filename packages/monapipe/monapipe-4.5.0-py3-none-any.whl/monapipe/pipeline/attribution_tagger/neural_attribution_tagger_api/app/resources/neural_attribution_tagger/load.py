# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os

from resource_handler import ResourceHandler
from tensorflow.keras import Sequential, models

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Sequential:
    """Loading method of the `neural_attribution_tagger` resource.

    Returns:
        The model.

    """
    model = models.load_model(
        os.path.join(RESOURCE_HANDLER.data_path, "attribution", "no_encoding")
    )
    return model

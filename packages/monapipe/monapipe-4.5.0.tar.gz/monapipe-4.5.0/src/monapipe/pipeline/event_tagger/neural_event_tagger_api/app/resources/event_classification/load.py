# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
import os
import subprocess
import sys
from typing import Tuple

from resource_handler import ResourceHandler
from transformers import ElectraPreTrainedModel, ElectraTokenizer

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Tuple[ElectraPreTrainedModel, ElectraTokenizer]:
    """Loading method of the `event_classification` resource.

    Returns:
        Model.
        Tokenizer.

    """
    # load catma_gitlab
    try:
        import catma_gitlab  # pylint: disable=import-outside-toplevel, unused-import
    except ImportError:
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "git+https://github.com/hatzel/catma_gitlab.git@54011e3f",
                ]
            )
        except Exception as e:
            error_msg = (f"Installation of catma_gitlab has failed with error message: {e}\n") + (
                "Please install `catma_gitlab` via "
                + "`pip install git+https://github.com/hatzel/catma_gitlab.git@54011e3f`"
                + " into your Python environment and run your previous code again."
            )
            raise Exception(error_msg)

    # load event classifier
    sys.path.append(
        RESOURCE_HANDLER.data_path
    )  # necessary because there are some relative imports in `event_classify`
    path = ".".join(["data", "event_classification", "event_classify", "util"])
    module = importlib.import_module(path)
    model_path = os.path.join(RESOURCE_HANDLER.data_path, "demo_model")
    model, tokenizer = module.get_model(model_path)
    sys.path.remove(RESOURCE_HANDLER.data_path)
    return model, tokenizer

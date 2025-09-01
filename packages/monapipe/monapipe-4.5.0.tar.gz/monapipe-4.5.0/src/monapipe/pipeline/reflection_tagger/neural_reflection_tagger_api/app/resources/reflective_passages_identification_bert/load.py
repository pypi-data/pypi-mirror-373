# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
import os
import sys
from typing import Any, Dict

from config import SETTINGS
from resource_handler import ResourceHandler
from transformers import AutoTokenizer

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Dict[str, Any]:
    """Loading method of the `reflective_passages_identification_bert`/
        `generalizing_passages_identification_bert` resource.

    Returns:
        Dictionary mapping a label scheme to the corresponding model.
            The label schemes are: "gi_binary", "gi_multi", "reflexive_binary", "reflexive_multi".

    """
    sys.path.append(
        os.path.join(RESOURCE_HANDLER.data_path, "src")
    )  # necessary because there are some relative imports in `src`
    name = RESOURCE_HANDLER.data_path.strip(os.path.sep).split(os.path.sep)[-1]
    path = ".".join(["data", name, "src"])
    module_ml_model_util = importlib.import_module(path + ".ml.model_util")
    module_xai_prediction_pipeline = importlib.import_module(path + ".xai.prediction_pipeline")

    saved_models = {
        "gi_binary": "binary_gbert-large_monaco_epochs_20_lamb_0.0001_None_dh_0.3_da_0.0.pt",
        "gi_multi": "multi_gbert-large_monaco_epochs_20_lamb_0.0001_None_dh_0.3_da_0.0.pt",
        "reflexive_binary": "reflexive_ex_mk_binary_gbert-large_monaco-ex-kleist_epochs_20_lamb_0.0001_None_dh_0.3_da_0.0.pt",
        "reflexive_multi": "reflexive_ex_mk_multi_gbert-large_monaco-ex-kleist_epochs_20_lamb_0.0001_None_dh_0.3_da_0.0.pt",
    }
    model_labels = {
        "gi_binary": ["generalization"],
        "gi_multi": ["none", "ALL", "BARE", "DIV", "EXIST", "MEIST", "NEG"],
        "reflexive_binary": ["reflexive"],
        "reflexive_multi": ["gi", "comment", "nfr_ex_mk"],
    }

    pretrained_model_str = "deepset/gbert-large"
    evaluation_tokenizer = AutoTokenizer.from_pretrained(pretrained_model_str)
    device = SETTINGS["torch_device"]

    prediction_pipelines = {}
    for name, saved_model in saved_models.items():
        saved_model_path = os.path.join(
            RESOURCE_HANDLER.data_path, "output", "saved_models", saved_model
        )
        if os.path.exists(saved_model_path):
            labels = model_labels[name]
            fine_tuned_model = module_ml_model_util.load_model(
                model_path=saved_model_path,
                device=device,
                petrained_model_str=pretrained_model_str,
                no_labels=len(labels),
            )
            prediction_pipelines[name] = module_xai_prediction_pipeline.PredictionPipeline(
                fine_tuned_model, evaluation_tokenizer, 206, device, labels
            )

    sys.path.remove(os.path.join(RESOURCE_HANDLER.data_path, "src"))

    return prediction_pipelines

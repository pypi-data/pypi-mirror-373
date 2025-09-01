# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Optional, Union

resources = importlib.import_module("resource_handler")
config = importlib.import_module("config")

from config import SETTINGS
from torch.utils.data import DataLoader

_device = SETTINGS["torch_device"]

AnnotationsTypeInput = List[Dict[str, Union[int, List[List[int]], Optional[str]]]]
AnnotationsTypeOutput = List[
    Dict[str, Union[int, List[List[int]], str, Dict[str, Union[str, Optional[bool]]]]]
]


def request_neural_event_tagger(
    data_dict: Dict[str, Union[str, AnnotationsTypeInput, Optional[str]]]
) -> Dict[str, Union[str, AnnotationsTypeOutput, Optional[str]]]:
    """Request neural event tagger.

    Args:
        data_dict (Dict): Input dictionary with the following keys:
            - text (str): The main text to be processed.
            - title (str | None): Optional title of the text.
            - annotations (List[Dict]): A list of annotation dictionaries, each containing:
                - start (int): Start index of the annotation.
                - end (int): End index of the annotation.
                - spans (List[List[int]]): List of span indices.
                - predicted (str | None): Predicted annotation.

    Returns:
        `data_dict` with processed data (annotations with predictions):
            - text (str): The main text to be processed.
            - title (str | None): Optional title of the text.
            - annotations (List[Dict]): A list of annotation dictionaries, each containing:
                - start (int): Start index of the annotation.
                - end (int): End index of the annotation.
                - spans (List[List[int]]): List of span indices.
                - predicted (str | None): Predicted annotation.
                - additional_predictions (Dict): Additional predictions for the annotation
                    - event_types (str): Event type.
                    - speech_type (str): Speech type.
                    - thought_representation (bool): Thought representation.
                    - iterative (bool): Iterative.
                    - mental (bool): Mental.
    """
    model, tokenizer = resources.access("event_classification")

    path = ".".join(["data", "event_classification", "event_classify"])
    module_datasets = importlib.import_module(path + ".datasets")
    module_eval = importlib.import_module(path + ".eval")

    special_tokens = True
    batch_size = 8

    dataset = module_datasets.JSONDataset(
        dataset_file=None, data=[data_dict], include_special_tokens=special_tokens
    )
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        collate_fn=lambda list_: module_datasets.SpanAnnotation.to_batch(list_, tokenizer),
    )

    model.to(_device)
    result = module_eval.evaluate(loader, model, device=_device)
    data = dataset.get_annotation_json(result)[0]

    return data

# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Optional, Union

from fastapi import Body, FastAPI
from request_neural_event_tagger import (
    AnnotationsTypeInput,
    AnnotationsTypeOutput,
    request_neural_event_tagger,
)

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "neural_event_tagger_api based on FastAPI."}


@app.post("/neural_event_tagger_api/")
def apply_neural_event_tagger(
    data_dict: Dict[str, Union[str, AnnotationsTypeInput, Optional[str]]] = Body(...,
    examples={
        "input_example": {
            "text": "Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt.",
            "annotations": [
                {"start": 0, "end": 53, "spans": [(0, 53)], "predicted": None},
                {"start": 63, "end": 86, "spans": [(63, 86)], "predicted": None},
                {"start": 91, "end": 123, "spans": [(91, 123)], "predicted": None},
                {"start": 0, "end": 53, "spans": [(0, 53)], "predicted": None},
                {"start": 63, "end": 86, "spans": [(63, 86)], "predicted": None},
                {"start": 91, "end": 123, "spans": [(91, 123)], "predicted": None},
            ],
            "title": None,
        },
        "output_example": {
            "title": None,
            "text": "Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt.",
            "annotations": [
                {
                    "start": 0,
                    "end": 53,
                    "spans": [[0, 53]],
                    "predicted": "change_of_state",
                    "predicted_score": 7,
                    "additional_predictions": {
                        "event_types": "change_of_state",
                        "speech_type": "narrator",
                        "thought_representation": True,
                        "iterative": False,
                        "mental": True,
                    },
                },
                {
                    "start": 0,
                    "end": 53,
                    "spans": [[0, 53]],
                    "predicted": "change_of_state",
                    "predicted_score": 7,
                    "additional_predictions": {
                        "event_types": "change_of_state",
                        "speech_type": "narrator",
                        "thought_representation": True,
                        "iterative": False,
                        "mental": True,
                    },
                },
                {
                    "start": 63,
                    "end": 86,
                    "spans": [[63, 86]],
                    "predicted": "change_of_state",
                    "predicted_score": 7,
                    "additional_predictions": {
                        "event_types": "change_of_state",
                        "speech_type": "narrator",
                        "thought_representation": True,
                        "iterative": False,
                        "mental": True,
                    },
                },
                {
                    "start": 63,
                    "end": 86,
                    "spans": [[63, 86]],
                    "predicted": "change_of_state",
                    "predicted_score": 7,
                    "additional_predictions": {
                        "event_types": "change_of_state",
                        "speech_type": "narrator",
                        "thought_representation": True,
                        "iterative": False,
                        "mental": True,
                    },
                },
                {
                    "start": 91,
                    "end": 123,
                    "spans": [[91, 123]],
                    "predicted": "change_of_state",
                    "predicted_score": 7,
                    "additional_predictions": {
                        "event_types": "change_of_state",
                        "speech_type": "narrator",
                        "thought_representation": True,
                        "iterative": False,
                        "mental": True,
                    },
                },
                {
                    "start": 91,
                    "end": 123,
                    "spans": [[91, 123]],
                    "predicted": "change_of_state",
                    "predicted_score": 7,
                    "additional_predictions": {
                        "event_types": "change_of_state",
                        "speech_type": "narrator",
                        "thought_representation": True,
                        "iterative": False,
                        "mental": True,
                    },
                },
            ],
        },
    }),
) -> Dict[str, Union[str, AnnotationsTypeOutput, Optional[str]]]:
    """Apply neural event tagger.

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
    neural_event_tagger = request_neural_event_tagger(data_dict=data_dict)
    return neural_event_tagger

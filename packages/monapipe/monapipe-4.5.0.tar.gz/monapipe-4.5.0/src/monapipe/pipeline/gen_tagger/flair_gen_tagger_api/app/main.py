# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Optional, Set, Union

from fastapi import Body, FastAPI
from request_flair_gen_tagger import request_flair_gen_tagger

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "flair_gen_tagger_api based on FastAPI."}


@app.post(
    "/flair_gen_tagger_api/",
    responses={
        200: {
            "description": "Succesful response.",
            "content": {
                "application/json": {
                    "example": {
                        "flair_gen_tagger": {
                            0: set(),
                            1: set(),
                            2: set(),
                            3: set(),
                            4: {"ALL"},
                            5: {"ALL"},
                        },
                    }
                }
            },
        }
    },
)
def apply_flair_gen_tagger(
    sentence: List[Dict[str, Union[str, Optional[int], bool]]] = Body(...),
    example=[
        {"text": "Old", "clause": 0, "is_space": False},
        {"text": "Death", "clause": 0, "is_space": False},
        {"text": "!", "clause": None, "is_space": False},
        {"text": "Ah", "clause": 1, "is_space": False},
        {"text": ",", "clause": 1, "is_space": False},
        {"text": "dieser", "clause": 1, "is_space": False},
        {"text": "Mann", "clause": 1, "is_space": False},
        {"text": "war", "clause": 1, "is_space": False},
        {"text": "Old", "clause": 1, "is_space": False},
        {"text": "Death", "clause": 1, "is_space": False},
        {"text": "!", "clause": None, "is_space": False},
        {"text": "Ich", "clause": 2, "is_space": False},
        {"text": "hatte", "clause": 2, "is_space": False},
        {"text": "von", "clause": 2, "is_space": False},
        {"text": "diesem", "clause": 2, "is_space": False},
        {"text": "bekannten", "clause": 2, "is_space": False},
        {"text": ",", "clause": None, "is_space": False},
        {"text": "ja", "clause": 3, "is_space": False},
        {"text": "berühmten", "clause": 3, "is_space": False},
        {"text": "Westmanne", "clause": 3, "is_space": False},
        {"text": "oft", "clause": 3, "is_space": False},
        {"text": "gehört", "clause": 3, "is_space": False},
        {"text": ".", "clause": None, "is_space": False},
        {"text": "Sein", "clause": 4, "is_space": False},
        {"text": "Ruf", "clause": 4, "is_space": False},
        {"text": "war", "clause": 4, "is_space": False},
        {"text": "an", "clause": 4, "is_space": False},
        {"text": "allen", "clause": 4, "is_space": False},
        {"text": "Lagerfeuern", "clause": 4, "is_space": False},
        {"text": "jenseits", "clause": 4, "is_space": False},
        {"text": "des", "clause": 4, "is_space": False},
        {"text": "Mississippi", "clause": 4, "is_space": False},
        {"text": "erklungen", "clause": 4, "is_space": False},
        {"text": "und", "clause": 5, "is_space": False},
        {"text": "auch", "clause": 5, "is_space": False},
        {"text": "bis", "clause": 5, "is_space": False},
        {"text": "in", "clause": 5, "is_space": False},
        {"text": "die", "clause": 5, "is_space": False},
        {"text": "Städte", "clause": 5, "is_space": False},
        {"text": "des", "clause": 5, "is_space": False},
        {"text": "Ostens", "clause": 5, "is_space": False},
        {"text": "gedrungen", "clause": 5, "is_space": False},
        {"text": ".", "clause": None, "is_space": False},
    ],
) -> Dict[str, Dict[int, Set[str]]]:
    """Apply flair gen tagger to a sentence.

    Args:
        sentence: The sentence as a list of token dictionaries.

    Returns:
        Dictionary with the labels assigned by the flair gen tagger for each clause.

    """
    flair_gen_tagger = request_flair_gen_tagger(sentence)
    return {"flair_gen_tagger": flair_gen_tagger}

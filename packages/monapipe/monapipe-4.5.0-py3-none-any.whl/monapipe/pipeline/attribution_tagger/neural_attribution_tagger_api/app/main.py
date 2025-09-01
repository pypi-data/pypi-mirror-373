# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Optional, Union

from fastapi import Body, FastAPI
from request_neural_attribution_tagger import request_neural_attribution_tagger

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "neural_attribution_tagger_api based on FastAPI."}


@app.post("/neural_attribution_tagger_api/")
def apply_neural_attribution_tagger(
    sentences: List[List[Dict[str, Union[str, Optional[int]]]]] = Body(...),
    example=[
        [
            {"text": "Eduard", "clause": 0},
            {"text": "–", "clause": None},
            {"text": "so", "clause": 1},
            {"text": "nennen", "clause": 1},
            {"text": "wir", "clause": 1},
            {"text": "einen", "clause": 1},
            {"text": "reichen", "clause": 1},
            {"text": "Baron", "clause": 1},
            {"text": "im", "clause": 1},
            {"text": "besten", "clause": 1},
            {"text": "Mannesalter", "clause": 1},
            {"text": "–", "clause": None},
            {"text": "Eduard", "clause": 2},
            {"text": "hatte", "clause": 2},
            {"text": "in", "clause": 2},
            {"text": "seiner", "clause": 2},
            {"text": "Baumschule", "clause": 2},
            {"text": "die", "clause": 2},
            {"text": "schönste", "clause": 2},
            {"text": "Stunde", "clause": 2},
            {"text": "eines", "clause": 2},
            {"text": "Aprilnachmittags", "clause": 2},
            {"text": "zugebracht", "clause": 2},
            {"text": ",", "clause": None},
            {"text": "um", "clause": 3},
            {"text": "frisch", "clause": 3},
            {"text": "erhaltene", "clause": 3},
            {"text": "Pfropfreiser", "clause": 3},
            {"text": "auf", "clause": 3},
            {"text": "junge", "clause": 3},
            {"text": "Stämme", "clause": 3},
            {"text": "zu", "clause": 3},
            {"text": "bringen", "clause": 3},
            {"text": ".", "clause": None},
        ],
        [
            {"text": "Sein", "clause": 0},
            {"text": "Geschäft", "clause": 0},
            {"text": "war", "clause": 0},
            {"text": "eben", "clause": 0},
            {"text": "vollendet", "clause": 0},
            {"text": ";", "clause": None},
            {"text": "er", "clause": 1},
            {"text": "legte", "clause": 1},
            {"text": "die", "clause": 1},
            {"text": "Gerätschaften", "clause": 1},
            {"text": "in", "clause": 1},
            {"text": "das", "clause": 1},
            {"text": "Futteral", "clause": 1},
            {"text": "zusammen", "clause": 1},
            {"text": "und", "clause": 2},
            {"text": "betrachtete", "clause": 2},
            {"text": "seine", "clause": 2},
            {"text": "Arbeit", "clause": 2},
            {"text": "mit", "clause": 2},
            {"text": "Vergnügen", "clause": 2},
            {"text": ",", "clause": None},
            {"text": "als", "clause": 3},
            {"text": "der", "clause": 3},
            {"text": "Gärtner", "clause": 3},
            {"text": "hinzutrat", "clause": 3},
            {"text": "und", "clause": 4},
            {"text": "sich", "clause": 4},
            {"text": "an", "clause": 4},
            {"text": "dem", "clause": 4},
            {"text": "teilnehmenden", "clause": 4},
            {"text": "Fleiße", "clause": 4},
            {"text": "des", "clause": 4},
            {"text": "Herrn", "clause": 4},
            {"text": "ergetzte", "clause": 4},
            {"text": ".", "clause": None},
        ],
        [
            {"text": "»", "clause": None},
            {"text": "Hast", "clause": 0},
            {"text": "du", "clause": 0},
            {"text": "meine", "clause": 0},
            {"text": "Frau", "clause": 0},
            {"text": "nicht", "clause": 0},
            {"text": "gesehen", "clause": 0},
            {"text": "?", "clause": None},
            {"text": "«", "clause": None},
            {"text": "fragte", "clause": 1},
            {"text": "Eduard", "clause": 1},
            {"text": ",", "clause": None},
            {"text": "indem", "clause": 2},
            {"text": "er", "clause": 2},
            {"text": "sich", "clause": 2},
            {"text": "weiterzugehen", "clause": 2},
            {"text": "anschickte", "clause": 2},
            {"text": ".", "clause": None},
        ],
        [
            {"text": "»", "clause": None},
            {"text": "Drüben", "clause": 0},
            {"text": "in", "clause": 0},
            {"text": "den", "clause": 0},
            {"text": "neuen", "clause": 0},
            {"text": "Anlagen", "clause": 0},
            {"text": "«", "clause": 0},
            {"text": ",", "clause": 0},
            {"text": "versetzte", "clause": 0},
            {"text": "der", "clause": 0},
            {"text": "Gärtner", "clause": 0},
            {"text": ".", "clause": None},
        ],
        [
            {"text": "»", "clause": None},
            {"text": "Die", "clause": 0},
            {"text": "Mooshütte", "clause": 0},
            {"text": "wird", "clause": 0},
            {"text": "heute", "clause": 0},
            {"text": "fertig", "clause": 0},
            {"text": ",", "clause": None},
            {"text": "die", "clause": 1},
            {"text": "sie", "clause": 1},
            {"text": "an", "clause": 1},
            {"text": "der", "clause": 1},
            {"text": "Felswand", "clause": 1},
            {"text": ",", "clause": 1},
            {"text": "dem", "clause": 1},
            {"text": "Schlosse", "clause": 1},
            {"text": "gegenüber", "clause": 1},
            {"text": ",", "clause": 1},
            {"text": "gebaut", "clause": 1},
            {"text": "hat", "clause": 1},
            {"text": ".", "clause": None},
        ],
    ],
) -> Dict[str, List[List[str]]]:
    """Apply neural attribution tagger to a document (list of sentences).

    Args:
        sentences: The document as a list of lists of token dictionaries.

    Returns:
        Dictionary with the labels assigned by the neural attribution tagger for each clause.

    """
    neural_attribution_tagger = request_neural_attribution_tagger(sentences)
    return {"neural_attribution_tagger": neural_attribution_tagger}

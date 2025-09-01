# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Tuple

from fastapi import Body, FastAPI
from request_bert_character_ner_api import request_bert_character_ner

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "bert_character_ner based on FastAPI."}


@app.post("/bert_character_ner_api/")
def apply_bert_character_ner(
    sentences: List[List[Tuple[str, int]]] = Body(...),
    example=[
        [("»", 0), ("Gandalf", 1), (",", 2), ("Gandalf", 3), ("!", 4)],
        [
            ("Du", 5),
            ("lieber", 6),
            ("Himmel", 7),
            (",", 8),
            ("doch", 9),
            ("nicht", 10),
            ("der", 11),
            ("wandernde", 12),
            ("Zauberer", 13),
            (",", 14),
            ("der", 15),
            ("dem", 16),
            ("alten", 17),
            ("Tuk", 18),
            ("ein", 19),
            ("Paar", 20),
            ("magischer", 21),
            ("Diamantklammern", 22),
            ("verehrte", 23),
            (",", 24),
            ("die", 25),
            ("sich", 26),
            ("von", 27),
            ("selbst", 28),
            ("schlossen", 29),
            ("und", 30),
            ("sich", 31),
            ("niemals", 32),
            ("ohne", 33),
            ("Befehl", 34),
            ("lösten", 35),
            ("?", 36),
        ],
    ],
) -> Dict[int, str]:
    """Apply bert character ner.

    Args:
        sentences: List containing a sublist for each sentence; each sentence contains tuples of words and their global_ids.

    Returns:
        The BIO tags for each token.

    """
    token_bio = request_bert_character_ner(sentences)
    return token_bio

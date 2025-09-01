# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Optional, Union

from fastapi import FastAPI, Query
from request_flair_speech_tagger import request_flair_speech_tagger

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "flair_speech_tagger_api based on FastAPI."}


@app.get("/flair_speech_tagger_api/")
def apply_flair_speech_tagger(
    sentence: str = Query(..., min_length=1), speech_type: str = Query(..., min_length=1)
) -> Dict[str, Union[str, List[Dict[str, Union[str, Optional[float]]]]]]:
    """Apply flair speech tagger to a sentence.

    Args:
        sentence: The sentence in string format.
        speech_type: The speech type to tag.

    Returns:
        Dictionary with sentence and flair speech tagger call for sentence.

    """
    flair_speech_tagger = request_flair_speech_tagger(sentence, speech_type=speech_type)
    return {
        "sentence": sentence,
        "flair_speech_tagger": flair_speech_tagger,
    }

# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Optional

resources = importlib.import_module("resource_handler")
config = importlib.import_module("config")

import flair
import torch
from config import SETTINGS
from flair.data import Sentence
from flair.models import SequenceTagger

flair.device = torch.device(SETTINGS["torch_device"])


def request_flair_speech_tagger(
    sent_string: str, speech_type: str
) -> List[Dict[str, Optional[float]]]:
    """Request response tokens in a sentence.

    Args:
        sent_string: The sentence in string format.
        speech_type: The speech type to tag.

    Returns:
        List of dictionaries with token and score.

    """
    taggers = resources.access(resource_name="speech_taggers")

    sent_flair_format = Sentence(sent_string, use_tokenizer=False)
    taggers[speech_type].predict(sent_flair_format)
    score_list = []
    for i, token in enumerate(sent_flair_format.tokens):
        tag = sent_flair_format[i].get_labels()[0]
        if tag.value == speech_type:
            score_list.append({"token": token.text, "score": tag.score, "speech_type": speech_type})
        else:
            score_list.append({"token": token.text, "score": None, "speech_type": speech_type})

    return score_list

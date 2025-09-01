# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Optional, Union

resources = importlib.import_module("resource_handler")
config = importlib.import_module("config")


def request_raum_space_tagger(data_dict: Dict[str, Union[str, bool]]) -> Dict[str, Union[List[str], List[List[Union[int, str]]]]]:
    """Request neural event tagger.

    Args:
        data_dict (Dict): Input dictionary with the following keys:
            - text (str): The main text to be processed.
            - with_metaphors (bool): Whether to include metaphors in the processing.

    Returns:
        Dict: A dictionary containing the following keys:
            - "corenlp_tokens": A list of tokens from the CoreNLP annotations.
            - "start_end_label_tuple": A list of tuples, each containing the start and end indices of a mention
              and the corresponding label (space type).
    """
    with_metaphors = data_dict["with_metaphors"]
    text = data_dict["text"]

    clients = resources.access("raum_classifier")
    client = clients[("" if with_metaphors else "_ohneMetaphern")]

    annotations = client.annotate(text)

    corenlp_tokens = [token.value for sentence in annotations.sentence for token in sentence.token]

    return {
        "corenlp_tokens": corenlp_tokens,
        "start_end_label_tuple": [(mention.tokenStartInSentenceInclusive, mention.tokenEndInSentenceExclusive, mention.ner.replace(" ", "_")) for sentence in annotations.sentence for mention in sentence.mentions],
    }

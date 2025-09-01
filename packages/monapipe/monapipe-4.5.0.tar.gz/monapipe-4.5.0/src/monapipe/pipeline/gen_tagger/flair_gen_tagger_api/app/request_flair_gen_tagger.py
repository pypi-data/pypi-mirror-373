# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Optional, Set, Union

import transformers
from flair.data import Sentence
from flair.models import SequenceTagger

resources = importlib.import_module("resource_handler")


def get_clause_labels(
    sent: List[Dict[str, Union[str, Optional[int], bool]]], tagger: SequenceTagger
) -> Dict[int, Set[str]]:
    """Get the labels for each clause in a sentence.

    Args:
        sent: The sentence as a list of token dictionaries.
        tagger: The flair tagger model.

    Returns:
        A dictionary that maps clauses to labels.

    """
    tagger = resources.access("flair_gen_tagger_cv")
    text = " ".join([token["text"] for token in sent if not token["is_space"]])
    text = Sentence(text, use_tokenizer=False)
    try:
        try:
            tagger.predict(text)
        except AttributeError:
            # The `flair` models were trained with an earlier version of `transformers`,
            # where some attributes did not exist that are now expected.
            # These attributes are set here:
            transformers.models.bert.tokenization_bert.BasicTokenizer.do_split_on_punc = True
            transformers.models.bert.tokenization_bert.BertTokenizer._added_tokens_encoder = {}
            transformers.tokenization_utils.PreTrainedTokenizer.split_special_tokens = False
            tagger.predict(text)
        clause_tags = {token["clause"]: {} for token in sent if token["clause"] is not None}
        clause_tokens = {
            clause: [token for token in sent if token["clause"] == clause] for clause in clause_tags
        }
        s = 0
        for i, token in enumerate(sent):
            if token["is_space"]:
                s += 1
            else:
                tag = text.tokens[i - s].get_labels()[0].value
                if tag != "-":
                    if token["clause"] is not None:
                        if tag not in clause_tags[token["clause"]]:
                            clause_tags[token["clause"]][tag] = 0
                        clause_tags[token["clause"]][tag] += 1
        for clause in clause_tags:
            clause_tags[clause] = set(
                [
                    tag
                    for tag in clause_tags[clause]
                    if 1.0 * clause_tags[clause][tag] / len(clause_tokens[clause]) >= 0.5
                ]
            )
        return clause_tags
    except RuntimeError:  # input sequence too long
        return {token["clause"]: set() for token in sent if token["clause"] is not None}


def request_flair_gen_tagger(
    sent: List[Dict[str, Union[str, Optional[int], bool]]]
) -> Dict[int, Set[str]]:
    """Request flair gen tagger.

    Args:
        sent: The sentence as a list of token dictionaries.

    Returns:
        Dictionary with the labels assigned by the flair gen tagger for each clause.

    """
    model = resources.access("flair_gen_tagger_cv")
    return get_clause_labels(sent, model)

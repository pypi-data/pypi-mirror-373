# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Tuple

resources = importlib.import_module("resource_handler")
config = importlib.import_module("config")

import gc
from itertools import chain

import numpy as np
import torch
from config import HUGGINGFACE_HUB, SETTINGS
from more_itertools import constrained_batches
from transformers import AutoModelForTokenClassification, AutoTokenizer

_device = SETTINGS["torch_device"]
_model = AutoModelForTokenClassification.from_pretrained(
    **HUGGINGFACE_HUB["fiction-gbert-char-ner"]
)

_id2label = {v: k for k, v in _model.config.label2id.items()}
_tokenizer = AutoTokenizer.from_pretrained(**HUGGINGFACE_HUB["fiction-gbert-char-ner"])


def _chunk_doc(sentences: List[List[Tuple[str, int]]]) -> Tuple[List[float], List[int]]:
    """Segment a doc into segments

    Args:
        sentences: List containing a sublist for each sentence; each sentence contains tuples of words and their global_ids.

    Returns:
        _description_

    """

    # Batch while respecting sentence boundaries
    def batch_length(sentence):
        s = [t[0] for t in sentence]
        return len(_tokenizer(s, is_split_into_words=True)["input_ids"])

    batches = constrained_batches(
        sentences, max_size=_tokenizer.model_max_length, get_len=batch_length
    )

    batches = [list(chain(*sentences)) for sentences in batches]
    return batches


def _idle():
    """Moves model to CPU after run."""
    if str(_model.device).startswith("cuda"):
        _model.to("cpu")
        torch.cuda.empty_cache()
        gc.collect()


def _wake_up():
    """Puts model on run-device"""
    if str(_model.device) != _device:
        try:
            _model.to(_device)
        except RuntimeError:
            _model.to("cpu")


def request_bert_character_ner(sentences: List[List[Tuple[str, int]]]) -> Dict[int, str]:
    """Tags literary characters in the document.

    Args:
        sentences: List containing a sublist for each sentence; each sentence contains tuples of words and their global_ids.

    Returns:
        The BIO tags for each token.

    """
    token_bio = {}
    _wake_up()
    chunks = _chunk_doc(sentences)
    for chunk in chunks:
        # Prepare data to align predictions with doc
        tokens, global_ids = list(zip(*chunk))

        # Get predictions
        inputs = _tokenizer(tokens, is_split_into_words=True, return_tensors="pt")
        with torch.no_grad():
            outputs = _model(**inputs.to(_model.device))
            logits = outputs["logits"].view(-1, 3).cpu().numpy()

        # Aggregate subword-token logits to word-level and annotate tokens in doc
        word_ids = np.array([i if i is not None else -100 for i in inputs.word_ids()])
        for word_id in set(word_ids.tolist()):
            if word_id == -100:
                continue

            # Average decoding
            # final_logits = logits[word_id == word_ids].reshape(-1, 3).mean(axis=0)

            # Max decoding
            # final_logits = logits[word_id == word_ids].reshape(-1, 3).max(axis=0)

            # First subword representative decoding
            final_logits = logits[word_id == word_ids].reshape(-1, 3)[0, :]

            prediction = _id2label[final_logits.argmax().item()]
            global_id = global_ids[word_id]
            token_bio[global_id] = prediction
    _idle()
    return token_bio

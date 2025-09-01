# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
from typing import Tuple

from huggingface_hub import snapshot_download
from resource_handler import ResourceHandler
from transformers import BertModel, BertTokenizer

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Tuple[BertModel, BertTokenizer]:
    """Loading method of the `dbmdz/bert-base-german-cased` tokenizer and model.

    Returns:
        The tokenizer.
        The model.

    """
    snapshot_download(repo_id="dbmdz/bert-base-german-cased", local_dir=RESOURCE_HANDLER.data_path)
    tokenizer = BertTokenizer.from_pretrained(RESOURCE_HANDLER.data_path)
    model = BertModel.from_pretrained(RESOURCE_HANDLER.data_path, output_hidden_states=True)
    return tokenizer, model

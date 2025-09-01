# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Union

resources = importlib.import_module("resource_handler")


def request_neural_gen_tagger(
    clause_text_embed_in_context: str, label_condition: str
) -> Dict[str, Union[str, List[int]]]:
    """Request neural gen tagger.

    Args:
        clause_text_embed_in_context (str): The clause text (marked with <b> tags) embedded in context.
        label_condition (str): Label condition ("multi" or "binary").

    Returns:
        Dictionary with clause text (surrounded by context) and
        neural gen tagger prediction for clause text.
    """
    models = resources.access("generalizing_passages_identification_bert")
    model = models["gi_" + label_condition]

    prediction = [round(x) for x in model.predict(clause_text_embed_in_context)]

    return prediction

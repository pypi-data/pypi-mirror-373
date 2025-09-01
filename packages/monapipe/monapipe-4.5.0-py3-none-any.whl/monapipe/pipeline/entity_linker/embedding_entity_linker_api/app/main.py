# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Optional, Union

import numpy as np
from fastapi import Body, FastAPI
from request_embedding_entity_linker import request_embedding_entity_linker

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "embedding_entity_linker_api based on fastText."}


@app.post("/embedding_entity_linker_api/")
def apply_embedding_entity_linker(
    input_data: Dict[str, List[str]] = Body(...)
) -> List[Dict[str, Union[str, Optional[float]]]]:
    """Calculate entity embedding similarity between entity candidates and embedding created from input terms.

    Args:
        input_data: dictionary containing two lists: under key "input_context", the input terms for which an embedding will be created and under key "name_variants", 
        the name variants of the input entity

    Returns:
        List of dictionaries with GND-ID and similarity score (or None if no candidate embedding existed).

    """
    result_embedding_entity_linker = request_embedding_entity_linker(input_data)
    return result_embedding_entity_linker
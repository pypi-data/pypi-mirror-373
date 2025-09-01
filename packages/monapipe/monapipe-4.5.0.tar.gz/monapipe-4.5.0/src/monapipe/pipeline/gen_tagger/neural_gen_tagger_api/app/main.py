# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Union

from fastapi import FastAPI, Query
from request_neural_gen_tagger import request_neural_gen_tagger

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "neural_gen_tagger_api based on FastAPI."}


@app.get(
    "/neural_gen_tagger_api/",
    responses={
        200: {
            "description": "Succesful response.",
            "content": {
                "application/json": {
                    "example": {
                        "clause_text_embed_in_context": "<b> Alle glücklichen Familien sind einander ähnlich,</b> jede unglückliche Familie ist unglücklich auf ihre Weise. Drunter und drüber ging es bei den Oblonskis",
                        "neural_gen_tagger": [1, 1, 1],
                    }
                }
            },
        }
    },
)
def apply_neural_gen_tagger(
    clause_text_embed_in_context: str = Query(
        ...,
        example="<b> Alle glücklichen Familien sind einander ähnlich,</b> jede unglückliche Familie ist unglücklich auf ihre Weise. Drunter und drüber ging es bei den Oblonskis",
    ),
    label_condition: str = Query(..., example="multi"),
) -> Dict[str, Union[str, List[int]]]:
    """Apply neural gen tagger to a clause surrounded by context.

    Args:
        clause_text_embed_in_context (str): The clause text (marked with <b> tags) embedded in context.
        label_condition (str): Label condition ("multi" or "binary").

    Returns:
        Dictionary with clause text (surrounded by context) and
        neural gen tagger prediction for clause text.
    """
    neural_gen_tagger = request_neural_gen_tagger(
        clause_text_embed_in_context=clause_text_embed_in_context, label_condition=label_condition
    )
    return {
        "clause_text_embed_in_context": clause_text_embed_in_context,
        "neural_gen_tagger": neural_gen_tagger,
    }

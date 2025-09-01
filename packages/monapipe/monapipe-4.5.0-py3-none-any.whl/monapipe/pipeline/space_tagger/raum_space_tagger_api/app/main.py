# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict, List, Union

from fastapi import Body, FastAPI
from request_raum_space_tagger import request_raum_space_tagger

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint.

    Returns:
        API message.
    """
    return {"message": "raum_space_tagger_api based on FastAPI."}


@app.post("/raum_space_tagger_api/")
def apply_raum_space_tagger(
    data_dict: Dict[str, Union[str, bool]] = Body(...,
    examples={
        "input_example": {
            "text": "Im südwestlichen Böhmen erhebt sich unweit der bayerischen Grenze ein Gebirge, das Böhmerwaldgebirge, aus Urgestein emporstarrend, mit Urwald bedeckt, darin viele Stellen sind, die noch nie ein Menschenfuß betreten hat. Der Wald zieht weithin in Bayern und Österreich hinüber und bildet einen der größten Waldkomplexe Mitteleuropas.",
            "with_metaphors": False,
        },
        "output_example": {
            'corenlp_tokens': 
                ['Im',
                 'südwestlichen', 
                 'Böhmen', 
                 'erhebt', 
                 'sich', 
                 'unweit', 
                 'der', 
                 'bayerischen', 
                 'Grenze', 
                 'ein', 
                 'Gebirge', 
                 ',', 
                 'das', 
                 'Böhmerwaldgebirge', 
                 ',', 
                 'aus', 
                 'Urgestein', 
                 'emporstarrend', 
                 ',', 
                 'mit', 
                 'Urwald', 
                 'bedeckt', 
                 ',', 
                 'darin', 
                 'viele', 
                 'Stellen', 
                 'sind', 
                 ',', 
                 'die', 
                 'noch', 
                 'nie', 
                 'ein', 
                 'Menschenfuß', 
                 'betreten', 
                 'hat', 
                 '.', 
                 'Der', 
                 'Wald', 
                 'zieht', 
                 'weithin', 
                 'in', 
                 'Bayern', 
                 'und', 
                 'Österreich', 
                 'hinüber', 
                 'und', 
                 'bildet', 
                 'einen', 
                 'der', 
                 'größten', 
                 'Waldkomplexe', 
                 'Mitteleuropas', 
                 '.'], 
            'start_end_label_tuple': 
                [[3, 4, 'RELATIONALES_VERB'],
                 [5, 6, 'RELATION'],
                 [8, 9, 'RAUMTHEMA'],
                 [10, 11, 'ORT'],
                 [13, 14, 'ORT'],
                 [20, 21, 'RAUMHINWEIS'],
                 [21, 22, 'RELATIONALES_VERB'],
                 [23, 24, 'RELATION'],
                 [25, 26, 'RAUMHINWEIS'],
                 [33, 34, 'RELATIONALES_VERB'],
                 [37, 38, 'ORT'],
                 [39, 41, 'RELATION'],
                 [41, 42, 'ORT'],
                 [43, 44, 'ORT'],
                 [44, 45, 'RELATION']]
        },
    }),
) -> Dict[str, Union[List[str], List[List[Union[int, str]]]]]:
    """Apply raum space tagger.

    Args:
        data_dict (Dict): Input dictionary with the following keys:
            - text (str): The main text to be processed.
            - with_metaphors (bool): Whether to include metaphors in the processing.

    Returns:
        Dict: A dictionary containing the following keys:
            - "corenlp_tokens": A list of tokens from the CoreNLP annotations.
            - "start_end_label_tuple": A list of tuples, each containing the start and end indices 
              of a mention and the corresponding label (space type).
    """
    raum_space_tagger = request_raum_space_tagger(data_dict=data_dict)
    return raum_space_tagger

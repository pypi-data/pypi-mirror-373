# SPDX-FileCopyrightText: 2025 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
from typing import Dict, List, Optional, Union

from thefuzz import fuzz

resources = importlib.import_module("resource_handler")
config = importlib.import_module("config")

import numpy as np
from numpy.linalg import norm


def request_embedding_entity_linker(
    input_data: Dict[str, List[str]]
) -> List[Dict[str, Union[str, Optional[float]]]]:
    """Request embedding and string similarities for an input context for which an embedding will be created and candidates with (optional) embeddings.

    Args:
        input_data: dictionary containing two lists: under key "input_context", the input terms for which an embedding will be created and under key "name_variants", 
        the name variants of the input entity

    Returns:
        List of dictionaries with GND-ID and scores for embedding and string similarities (emb_similarity can be None if no candidate embedding existed).

    """
    input_context = input_data["input_context"]
    input_names = input_data["input_name_variants"]

    # load the fasttext model, GND names and candidate entity embeddings
    fasttext_model, gnd_names, gnd_embeddings = resources.access("embedding_entity_linker")

    # find all possible GND candidates via their name variants
    candidate_ids = []
    candidate_names = {}

    for gnd_id_with_names in gnd_names:
        if not set(input_names).isdisjoint(gnd_id_with_names[1]):
            candidate_ids.append(gnd_id_with_names[0])
            if gnd_id_with_names[0] not in candidate_names:
                candidate_names[gnd_id_with_names[0]] = gnd_id_with_names[1]

    candidate_ids = list(set(candidate_ids))

    # for each candidate, retrieve their embedding
    candidate_embeddings = {}
    for c_id in candidate_ids:
        candidate_embeddings[c_id] = None
        if c_id in gnd_embeddings:
            candidate_embeddings[c_id] = gnd_embeddings[c_id]
    
    # calculate the input embedding
    input_embedding = np.mean([fasttext_model.get_word_vector(token) for token in input_context], 0)
    
    # calculate cosine similarities between input embedding and all candidate embeddings
    candidates_with_similarities = []
    for candidate_id in candidate_ids:
        if candidate_embeddings[candidate_id] is None:
            candidates_with_similarities.append({"GND-ID": candidate_id, "emb_similarity": None})
        else:
            entity_embedding = candidate_embeddings[candidate_id]
            cos_sim = np.dot(input_embedding, entity_embedding)/(norm(input_embedding)*norm(entity_embedding))
            candidates_with_similarities.append({"GND-ID": candidate_id, "emb_similarity": cos_sim})

    # sort candidates by embedding similarity
    candidates_with_similarities.sort(key=lambda a: a["emb_similarity"] if a["emb_similarity"] else -1000.0, reverse=True)

    # sort candidates by fuzzy string similarity, prioritized over embedding similarity
    candidates_with_similarities = _rank_candidates_string_sim(candidates_with_similarities, candidate_names, input_names[0])

    return candidates_with_similarities


def _rank_candidates_string_sim(emb_sim_ranked_candidates, candidate_names, entity_text):
    """
    Rerank candidates with string similarity (best of four different metrics) meeting a threshold before the embedding similarity rank.
    Candidates not reaching the threshold keep the order of the embedding similarity.
    
    Args:
        emb_sim_ranked_candidates: List of candidate dicts already ranked by embedding similarity.
        candidate_names: Dict of lists of names for the candidate entities.
        entity_text: text of how the entity appeared in the input (usually a name)
        
    Returns:
        Reranked list of candidate dicts, now also by string similarity if threshold was met.
    """
    sim_threshold = 70

    candidates_str_sim_above_threshold = []
    candidates_str_sim_below_threshold = []

    entity_text = entity_text.lower()

    for candidate in emb_sim_ranked_candidates:
        candidate_text = candidate_names[candidate["GND-ID"]][0].lower()

        candidate["str_similarity"] = _string_similarity(candidate_text, entity_text)

        if candidate["str_similarity"] >= sim_threshold:
            candidates_str_sim_above_threshold.append(candidate)
        else:
            candidates_str_sim_below_threshold.append(candidate)

    return candidates_str_sim_above_threshold + candidates_str_sim_below_threshold


def _string_similarity(candidate_text, entity_text):
    """
    Get the highest of four fuzzy string matching scores between candidate and entity name

    Args:
        candidate_text: str of the candidate (usually its name).
        entity_text: str of how the entity appeared in the input (usually its name).
        
    Returns:
        Similarity score between 0 and 100 (see thefuzz library documentation).
    """
    # remove common titles and double whitespaces
    for s in ["dr. ", "herr ", "frau ", "prof. "]:
        if entity_text.startswith(s):
            entity_text = entity_text[len(s):]

    entity_text = entity_text.replace('  ', ' ')

    # fuzzy matching
    scores = [
        fuzz.ratio(candidate_text, entity_text),
        fuzz.partial_ratio(candidate_text, entity_text),
        fuzz.token_sort_ratio(candidate_text, entity_text),
        fuzz.token_set_ratio(candidate_text, entity_text)
    ]

    # return best of the four scores
    return max(scores)

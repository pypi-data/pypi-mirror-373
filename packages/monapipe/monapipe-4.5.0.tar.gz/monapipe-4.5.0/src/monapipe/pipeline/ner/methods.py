# SPDX-FileCopyrightText: 2024 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Dict

from spacy.tokens import Doc, Span


def create_ents_from_token_bio(doc: Doc, token_bio: Dict[int, str], set_ents_mode: str):
    """Create named entity spans from token-level BIO entity tags.

    Args:
        doc: A document whose `.ents` attribute should be updated.
        token_bio: The BIO tags for each token.
        set_ents_mode: Specifies how the new entities should be added w.r.t. existing entities in `doc.ents`.
            - "r" or "reset": The new entities overwrite the existing entities.
            - "s" or "substitute": The new entities substitute existing entities of the same label(s). Existing entities with other labels remain unchanged.
            - "u" or "unify": The new entities are unified with the existing entities.

    """
    # get all new entity spans
    start = None
    spans = []
    for idx, token in enumerate(doc):
        if not token.text.strip():
            continue
        label = token_bio[idx]
        if label.startswith("O") and start is not None:
            spans.append(Span(doc, start, idx, token_bio[start].split("-")[1]))
            start = None
        if label.startswith("B"):
            if start is not None:
                spans.append(Span(doc, start, idx, token_bio[start].split("-")[1]))
            start = idx
    if start is not None:
        spans.append(Span(doc, start, len(doc), token_bio[start].split("-")[1]))

    if set_ents_mode in ["r", "reset"]:
        # reset/overwrite `doc.ents` with the new entities
        doc.set_ents(spans)

    elif set_ents_mode in ["s", "substitute"]:
        # first, add all entities from `doc.ents` that don't have any of the labels of the new entities;
        # second, add those new entities that don't overlap with the entities from the first group
        span_labels = set([span.label_ for span in spans])
        ents = [ent for ent in doc.ents if ent[0].ent_type_ not in span_labels]
        ent_tokens = set([token.i for ent in ents for token in ent])
        for span in spans:
            overlap = False
            for token in span:
                if token.i in ent_tokens:
                    overlap = True
                    break
            if not overlap:
                ents.append(span)
        doc.set_ents(ents)

    elif set_ents_mode in ["u", "unify"]:
        # first, add all new entities;
        # second, add those entities from `doc.ents` that don't overlap with the new entities
        span_tokens = set([token.i for span in spans for token in span])
        for ent in doc.ents:
            overlap = False
            for token in ent:
                if token.i in span_tokens:
                    overlap = True
                    break
            if not overlap:
                spans.append(ent)
        doc.set_ents(spans)

    else:
        raise ValueError('`set_ents_mode` must be "r(eset)", "s(ubstitute)" or "u(nify)".')

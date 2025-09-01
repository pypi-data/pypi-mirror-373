# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import itertools
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from spacy.tokens import Doc, Span, Token


def agreement(
    set1: Union[Set[str], List[str]], set2: Union[Set[str], List[str]], strict: bool = False
) -> bool:
    """Checks the agreement between two sets of values.

    Args:
        set1: A set of values.
        set2: A set of values.
        strict: If False, the agreement is true if one of the sets is empty.

    Returns:
        True iff either `strict=False` and one of the sets is empty, or the intersection of both sets is not empty.

    """
    set1 = set(set1)
    set2 = set(set2)
    if strict:
        return len(set1.intersection(set2)) > 0
    return len(set1) == 0 or len(set2) == 0 or len(set1.intersection(set2)) > 0


def get_attributes(span: Span, attr: str) -> Tuple[Any, ...]:
    """Get the values of a certain attribute for all tokens of a span.

    Args:
        span: A span.
        attr: The token attribute.

    Returns:
        The attribute values for every token as tuple.

    """
    return tuple([getattr(token, attr) for token in span])


def get_clauses(span: Span) -> List[Span]:
    """Returns the clauses of a span.
        If the document is not clausized, returns a list that only contains the span.

    Args:
        span: A span.

    Returns:
        The list of clauses in the span.

    """
    if not hasattr(span.doc._, "clauses"):
        return [span]
    clauses = []
    for token in span:
        if token._.clause is None:
            continue
        if token._.clause not in clauses:
            clauses.append(token._.clause)
    return clauses


def get_head_nouns(
    ent: Span, form: str = "text", lowercase: bool = True
) -> Tuple[List[str], List[str], List[str]]:
    """Get the nominal head and the modifiers (adjectives and numerals) of an entity.
        Examples:
            "den Spider-Man hassenden Zeitungsboss J.    Jonah Jameson"
             DET PROPN      ADJ       NOUN         PROPN PROPN PROPN
            -> [hassenden], [zeitungsboss], [j., jonah, jameson]

            "Peters betagter Onkel Ben"
             PROPN  ADJ      NOUN  PROPN
            -> [betagter], [onkel], [ben]

    Args:
        ent: An entity.
        form: The token attribute to use as string representation (e.g. "text" or "lemma_").
        lowercase: Whether the return strings should be lowercased.

    Returns:
        A list of (lowercased) modifiers.
        A list of (lowercased) common nouns.
        A list of (lowercased) proper nouns.

    """
    pos = get_attributes(ent, "pos_")
    propns = []
    nouns = []
    k = len(pos) - 1
    if "PROPN" in pos or "NOUN" in pos:
        while pos[k] not in ["PROPN", "NOUN"]:
            k -= 1
        if pos[k] == "PROPN":
            while k >= 0 and pos[k] == "PROPN":
                propns.append(k)
                k -= 1
        if "NOUN" in pos[: k + 1]:
            while k >= 0 and pos[k] != "NOUN":
                k -= 1
            while k >= 0 and pos[k] == "NOUN":
                nouns.append(k)
                k -= 1
        nouns = [w for k, w in enumerate(get_attributes(ent, form)) if k in nouns]
        propns = [w for k, w in enumerate(get_attributes(ent, form)) if k in propns]
    adjs = []
    while k >= 0 and pos[k] not in ["NUM", "ADJ", "NOUN", "PROPN"]:
        k -= 1
    while k >= 0 and pos[k] in ["ADJ", "NUM"]:
        adjs.append(k)
        k -= 1
    adjs = [w for k, w in enumerate(get_attributes(ent, form)) if k in adjs]
    if lowercase:
        adjs = [w.lower() for w in adjs]
        nouns = [w.lower() for w in nouns]
        propns = [w.lower() for w in propns]
    return adjs, nouns, propns


def get_morph_analyses(token: Token) -> List[Dict[str, str]]:
    """Get all possible morphological analyses of a token.
        Constructs the product over features from `token.morph`
        that have multiple comma-separated values.

    Args:
        token: The token.

    Returns:
        List of possible morphological analyses as feature dictionaries.
    """
    morph = token.morph.to_dict()
    analyses = []
    for feat, vals in morph.items():
        vals = vals.split(",")
        analyses.append([(feat, val) for val in vals])
    analyses = list(itertools.product(*analyses))
    return [dict(analysis) for analysis in analyses]


def get_morph_feat(span: Span, feat: str) -> Set[str]:
    """Get the value of morphological feature for a span.

    Args:
        span: A span.
        feat: The `MorphAnalysis` feature.

    Returns:
        Probable values.

    """
    # If the span's head has a single value for that feature, return it:
    val = span.root.morph.get(feat)
    if len(val) == 1:
        return set(val)

    values = [set(token.morph.get(feat)) for token in span]

    # Otherwise, if the intersection of the values of all tokens for that feature is not empty, return it:
    inters = set.intersection(*values)
    if len(inters) > 0:
        return inters

    # Otherwise, return the most frequent value(s) for that feature:
    values = [v for val in values for v in val]
    if len(values) > 0:
        values_counted = {val: values.count(val) for val in values}
        max_count = max(values_counted.values())
        return set([val for val, count in values_counted.items() if count == max_count])

    return set()


def get_noun_phrases(doclike: Union[Doc, Span]) -> List[Span]:
    """Returns all noun phrases in a text object.

    Args:
        doclike: A document or span (e.g. sentence).

    Returns:
        All noun phrases in the given text object -- named entities (.ents) and noun chunks (.noun_chunks).

    """
    ents = list(set(list(doclike.ents) + list(doclike.noun_chunks)))
    return sorted(ents, key=lambda ent: (ent.start, ent.end))


def is_common_noun(span: Span) -> bool:
    """There are three types of noun phrases:
        pronoun: a single word tagged as PRON
        proper noun: a span tagged as named entity or containing a proper noun
        common noun: any other span, usually a noun chunk

    Args:
        span: A span.

    Returns:
        boolean: True iff the span is a common noun.

    """
    return not (is_pronoun(span) or is_proper_noun(span))


def is_direct_speech(token: Union[Span, Token]) -> bool:
    """Check whether a span or token is within direct speech.

    Args:
        token: A span or token.

    Returns:
        boolean: True iff the span is within direct speech.
            Return False if the document has not been parsed by a speech tagger.

    """
    if not isinstance(token, Token):
        token = token.root
    if hasattr(token._, "speech"):
        return "direct" in token._.speech
    return False


def is_pronoun(span: Span) -> bool:
    """There are three types of noun phrases:
        pronoun: a single word tagged as PRON
        proper noun: a span tagged as named entity or containing a proper noun
        common noun: any other span, usually a noun chunk

    Args:
        span: A span.

    Returns:
        boolean: True iff the span is a pronoun.

    """
    pos = get_attributes(span, "pos_")
    return len(pos) == 1 and "PRON" in pos


def is_proper_noun(span: Span) -> bool:
    """There are three types of noun phrases:
        pronoun: a single word tagged as PRON
        proper noun: a span tagged as named entity or containing a proper noun
        common noun: any other span, usually a noun chunk

    Args:
        span: A span.

    Returns:
        boolean: True iff the span is a proper noun.

    """
    ent_iob = get_attributes(span, "ent_iob_")
    return "PROPN" in get_attributes(span, "pos") or "B" in ent_iob or "I" in ent_iob


def longest_common_prefix(str1, str2):
    """Return the longest common prefix of two strings.

    Args:
        str1 (str): A string.
        str2 (str): A string.

    Returns:
        str: Longest common prefix.

    """
    if str1.startswith(str2):
        return str2
    if str2.startswith(str1):
        return str1
    for i in range(min(len(str1), len(str2))):
        if str1[i] != str2[i]:
            return str1[:i]


def stringify(
    span: Span,
    form: str = "text",
    pos_: Optional[Union[Set[str], List[str]]] = None,
    lowercase: bool = True,
) -> str:
    """Converts a span to a text.

    Args:
        span: A span.
        form: The token attribute to use as string representation (e.g. "text" or "lemma_").
        pos_: List of allowed POS tags. If None, all POS tags are allowed.
        lowercase: Whether the return strings should be lowercased.

    Returns:
        str: The concatenated string representations of the tokens, separated by spaces.

    """
    pos = get_attributes(span, "pos_")
    words = " ".join(
        [w for k, w in enumerate(get_attributes(span, form)) if pos_ is None or pos[k] in pos_]
    )
    if lowercase:
        words = words.lower()
    return words

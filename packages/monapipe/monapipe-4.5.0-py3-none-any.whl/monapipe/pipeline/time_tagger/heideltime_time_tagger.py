# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import re
from typing import Any

from spacy.language import Language
from spacy.tokens import Doc

import monapipe.resource_handler as resources
from monapipe.pipeline.methods import update_token_span_groups
from monapipe.pipeline.time_tagger.time_tagger import TimeTagger


@Language.factory(
    "heideltime_time_tagger",
    assigns=TimeTagger.assigns,
    default_config={},
)
def heideltime_time_tagger(nlp: Language, name: str) -> Any:
    """Spacy component implementation.
        Adds time mentions to the document.
        Re-implementation of the algorithm presented in Strötgen & Gertz (2010):
        "HeidelTime: High Quality Rule-based Extraction and Normalization of Temporal Expressions".

    Args:
        nlp: Spacy object.
        name: Component name.

    Returns:
        `HeideltimeTimeTagger`.

    """
    return HeideltimeTimeTagger(nlp)


class HeideltimeTimeTagger(TimeTagger):
    """The class `HeideltimeTimeTagger`."""

    def __init__(self, nlp: Language):
        super().__init__(nlp)

    def __call__(self, doc: Doc) -> Doc:
        doc.spans["time"] = []

        # assign tokens to character positions for faster look-up
        charpos_to_token = {}
        for token in doc:
            for charpos in range(token.idx, token.idx + len(token.text_with_ws) + 1):
                charpos_to_token[charpos] = token

        ht_norms, ht_patterns, ht_rules = resources.access("heideltime")

        # find times
        matches = []
        for rules in ht_rules:
            for rule in ht_rules[rules]:
                extraction = rule["EXTRACTION"]
                for pattern in ht_patterns:
                    extraction = extraction.replace(
                        "%" + pattern,
                        "(" + ("|".join(ht_patterns[pattern])).replace("(", "(?:") + ")",
                    )
                for match in re.finditer(extraction, doc.text):
                    matches.append((match, rule))

        # sort matches by start and (descending) length
        matches = sorted(matches, key=lambda match: (match[0].start(), -match[0].end()))

        # remove matches that are contained in other matches (i.e. only keep maximal matches)
        matches_ = []
        spans = set()
        for match, rule in matches:
            covered = False
            for start, end in spans:
                if start <= match.start() and match.end() <= end:
                    covered = True
                    break
            if not covered:
                spans.add((match.start(), match.end()))
                matches_.append((match, rule))
        matches = matches_

        for match, rule in matches:
            # normalise time
            norm = rule["NORM_VALUE"]
            if norm == "REMOVE":
                # these are negative rules
                continue
            groups = list(match.groups())
            for i, group in enumerate(groups):
                if group is None:
                    group = ""
                norm = norm.replace("group(" + str(i + 1) + ")", group)
            for norms in ht_norms:
                if "%" + norms in norm:
                    for norms_ in ht_norms[norms]:
                        norm = re.sub(
                            "%" + norms + r"\(" + norms_ + r"\)", ht_norms[norms][norms_], norm
                        )
            for m in re.finditer(r"%SUBSTRING%\((.+?),(.+?),(.+?)\)", norm):
                norm = norm.replace(m.group(0), m.group(1)[int(m.group(2)) : int(m.group(3)) + 1])
            for m in re.finditer(r"%SUM%\((.+?),(.+?)\)", norm):
                norm = norm.replace(m.group(0), str(int(m.group(1)) + int(m.group(2))))
            for m in re.finditer(r"%UPPERCASE%\((.+?)\)", norm):
                norm = norm.replace(m.group(0), m.group(1).upper())

            # add additional norm values
            norm = {"NORM_VALUE": norm}
            for key in ["NORM_MOD", "NORM_QUANT", "NORM_FREQ"]:
                if key in rule:
                    norm[key] = rule[key]
            norm = {key[5:]: val for key, val in norm.items()}

            # map time to tokens
            start = charpos_to_token[match.start()]
            end = charpos_to_token[match.end() - 1]
            if not (match.start() == start.idx and match.end() == end.idx + len(end.text)):
                # prevent matches in the middle of words
                continue
            span = doc[start.i : end.i + 1]
            span._.time_norm = norm
            span._.time_type = rule["RULENAME"].split("_")[0].upper()
            doc.spans["time"].append(span)

        # sort times by start and length
        doc.spans["time"] = sorted(doc.spans["time"], key=lambda span: (span.start, span.end))

        update_token_span_groups(doc, ["time"])

        return doc

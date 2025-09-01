# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
from typing import Dict, List, Tuple

from monapipe.resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> (
    Tuple[Dict[str, Dict[str, str]], Dict[str, List[str]], Dict[str, List[Dict[str, str]]]]
):
    """Loading method of the `heideltime` resource.

    Returns:
        Normalisation rules.
            The first key corresponds to the filename; the second key is the search expression; the value is the replacement.
        Regex patterns.
            The key corresponds to the filename; the values are search expressions.
        Search and normalisation rules.
            The first key corresponds to the filename; the list corresponds to rules in that file; the second key corresponds to a rule property; the value is the value of that property.

    """
    language = "german"

    normalization = {}
    for filename in os.listdir(os.path.join(RESOURCE_HANDLER.data_path, language, "normalization")):
        normalization_ = {}
        with open(
            os.path.join(RESOURCE_HANDLER.data_path, language, "normalization", filename), "r"
        ) as f:
            for line in f.read().splitlines():
                if line != "" and not line.startswith("//"):
                    line = line.split(",")
                    normalization_[line[0][1:-1]] = line[1][1:-1]
        normalization[filename[len("resources_normalization_") : -4]] = normalization_

    repattern = {}
    for filename in os.listdir(os.path.join(RESOURCE_HANDLER.data_path, language, "repattern")):
        repattern_ = []
        with open(
            os.path.join(RESOURCE_HANDLER.data_path, language, "repattern", filename), "r"
        ) as f:
            for line in f.read().splitlines():
                if line != "" and not line.startswith("//"):
                    repattern_.append(line)
        repattern[filename[len("resources_repattern_") : -4]] = repattern_

    rules = {}
    for filename in os.listdir(os.path.join(RESOURCE_HANDLER.data_path, language, "rules")):
        rules_ = []
        with open(os.path.join(RESOURCE_HANDLER.data_path, language, "rules", filename), "r") as f:
            for line in f.read().splitlines():
                if line.startswith("RULENAME="):
                    parts = {}
                    if line.endswith(","):
                        line = line[:-1]
                    line = line[:-1]
                    line = line.split('",')
                    for part in line:
                        part = part.split('="')
                        parts[part[0]] = part[1]
                    rules_.append(parts)
        rules[filename[len("resources_rules_") : -4]] = rules_

    return (normalization, repattern, rules)

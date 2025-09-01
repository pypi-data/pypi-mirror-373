# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any, Callable, Dict, List, Union

from spacy.language import Language
from spacy.tokens import Doc, Span, Token

from monapipe.pipeline.methods import add_extension


class Formatter:
    """Component super class `Formatter`."""

    assigns = {"doc._.format_str": "doc._.format_str", "span._.format_str": "sent._.format_str"}

    def __init__(
        self,
        nlp: Language,
        column_names: List[str],
        column_names_plus: List[str],
        column_funcs: Union[str, Dict[str, Callable[[Token], Any]]],
        delimiter: str,
    ):
        self.column_names = column_names
        self.column_names_plus = column_names_plus
        self.column_funcs = column_funcs
        self.delimiter = delimiter

        add_extension(Doc, "format_str")
        add_extension(Span, "format_str")

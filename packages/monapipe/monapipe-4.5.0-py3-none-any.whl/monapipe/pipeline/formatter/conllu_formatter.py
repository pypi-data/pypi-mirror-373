# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import re
from typing import Any, Callable, Dict, List, Union

from spacy.language import Language
from spacy.tokens import Doc, Token

from monapipe.pipeline.formatter.formatter import Formatter
from monapipe.pipeline.methods import deserialize_config_param, optional


@Language.factory(
    "conllu_formatter",
    assigns=Formatter.assigns,
    default_config={
        "column_names": [
            "ID",
            "FORM",
            "LEMMA",
            "UPOS",
            "XPOS",
            "FEATS",
            "HEAD",
            "DEPREL",
            "DEPS",
            "MISC",
        ],
        "column_names_plus": [],
        "column_funcs": {},
        "delimiter": "\t",
    },
)
def conllu_formatter(
    nlp: Language,
    name: str,
    column_names: List[str],
    column_names_plus: List[str],
    column_funcs: Union[str, Dict[str, Callable[[Token], Any]]],
    delimiter: str,
) -> Any:
    """Spacy component implementation.
        Create a CoNLL-U Plus representation of the document.
        For more information see here: https://universaldependencies.org/ext-format.html

    Args:
        nlp: Spacy object.
        name: Component name.
        column_names: List of columns to be included.
            Per default, these are the 10 columns from the CoNLL-U format.
        column_names_plus: List of columns to be included.
            The complete list of columns will be `column_names` + `column_names_plus`.
        column_funcs: (Serialized) dictionary that maps a column name to a function that maps a token to a value.
            If there is a function given for one of the 10 default columns, the given function replaces the default one.
        delimiter: The column separator.
            If "\s+", a flexible number (at least 2) of spaces is inserted.
            Otherwise, the columns are concatenated using the given delimiter.

    Returns:
        `ConlluFormatter`.

    """
    return ConlluFormatter(nlp, column_names, column_names_plus, column_funcs, delimiter)


class ConlluFormatter(Formatter):
    """The class `ConlluFormatter`."""

    def __init__(
        self,
        nlp: Language,
        column_names: List[str],
        column_names_plus: List[str],
        column_funcs: Union[str, Dict[str, Callable[[Token], Any]]],
        delimiter: str,
    ):
        optional(self, nlp, ["parser"])

        super().__init__(nlp, column_names, column_names_plus, column_funcs, delimiter)

        self.column_names = self.column_names + self.column_names_plus

        column_funcs = deserialize_config_param(self.column_funcs)

        self.column_funcs = {
            "ID": lambda token: (
                list(token.sent).index(token) if token.doc.has_annotation("SENT_START") else token.i
            )
            + 1,
            "FORM": lambda token: (token._.text if hasattr(token._, "text") else token.text),
            "LEMMA": lambda token: token.lemma_,
            "UPOS": lambda token: token.pos_,
            "XPOS": lambda token: token.tag_,
            "FEATS": lambda token: token.morph,
            "HEAD": lambda token: (
                0
                if token.head == token
                else (
                    list(token.sent).index(token.head)
                    if token.doc.has_annotation("SENT_START")
                    else token.head.i
                )
                + 1
            ),
            "DEPREL": lambda token: token.dep_,
        }

        for column_name in column_funcs:
            self.column_funcs[column_name] = column_funcs[column_name]

    def __call__(self, doc: Doc) -> Doc:
        if doc.has_annotation("SENT_START"):
            sents = list(doc.sents)
        else:
            sents = [doc]
        first_row = "# global.columns = " + " ".join(self.column_names)
        doc_rows = []
        doc_char_widths = [-1] * len(self.column_names)
        for j, sent in enumerate(sents):
            sent_rows = []
            sent_char_widths = [-1] * len(self.column_names)
            try:
                sent_text = "".join([token._.text_with_ws for token in sent])
            except AttributeError:  # not normalized
                sent_text = "".join([token.text_with_ws for token in sent])
            sent_rows.append("# sent_id = " + str(j + 1))
            sent_rows.append("# text = " + re.sub(r"\s+", " ", sent_text).strip())
            for token in sent:
                row = []
                for i, column_name in enumerate(self.column_names):
                    val = self._apply_column_func(token, column_name)
                    val = self._format_value(val)
                    row.append(val)
                    sent_char_widths[i] = max(sent_char_widths[i], len(val))
                    doc_char_widths[i] = max(doc_char_widths[i], len(val))
                sent_rows.append(row)
            sent_rows.append("")
            doc_rows.extend(sent_rows)
            sent._.format_str = self._string_from_rows([first_row] + sent_rows, sent_char_widths)
        doc._.format_str = self._string_from_rows([first_row] + doc_rows, doc_char_widths)
        return doc

    def _apply_column_func(self, token: Token, column_name: str) -> Any:
        """Determine the value for the token in a given column.

        Args:
            token: The token.
            column_name: The name of the column.

        Returns:
            The value for the token in the given column;
                `None` if there is no corresponding value in the document.

        """
        if column_name in self.column_funcs:
            try:
                return self.column_funcs[column_name](token)
            except Exception:
                # the attribute cannot be computed for the token
                pass
        return None

    def _format_value(self, val: Any) -> str:
        """Stringify a value.

        Args:
            val: The value.

        Returns:
            A string that contains no linebreaks;
                "_" is used to represent unknown values.
                "*" is used to represent known but empty values.

        """
        if val is None:
            return "_"
        val = re.sub(r"\s+", " ", str(val)).strip()
        if val == "":
            return "*"
        return val

    def _string_from_rows(self, rows: List[Union[str, List[str]]], char_widths: List[int]) -> str:
        """Convert a list of rows into the final ConLL-U representation.

        Args:
            rows: The lines of the ConLL-U file.
                Comments and blank lines are already strings;
                    other lines are lists that contain the string values for each column.
            char_widths: The length of the longest string in each column.

        Returns:
            The ConLL-U string representation.

        """
        lines = []
        for row in rows:
            if isinstance(row, str):
                lines.append(row)
            else:
                if self.delimiter == "\s+":
                    lines.append(
                        "".join([val.ljust(char_widths[i] + 2) for i, val in enumerate(row)])
                    )
                else:
                    lines.append(self.delimiter.join(row))
        return "\n".join(lines)

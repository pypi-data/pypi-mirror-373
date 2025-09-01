# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import importlib
import warnings
from typing import Any


def lookup(lang: str, name: str) -> Any:
    """Returns language-specific data.

    Args:
        lang: The language.
        name: Name of the data.

    Returns:
        The data at `monapipe.lang.[lang].[name].[NAME]`.

    """
    path = ".".join(["monapipe", "lang", lang, name])
    data = name.upper()
    try:
        module = importlib.import_module(path)
        return getattr(module, data)
    except (AttributeError, ModuleNotFoundError):
        warnings.warn(
            "There is no data at '" + path + "." + data + "'. Return `{}` instead.", UserWarning
        )
        return {}

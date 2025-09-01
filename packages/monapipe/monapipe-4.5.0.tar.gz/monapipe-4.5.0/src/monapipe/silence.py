# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import logging
import os
import warnings
from functools import partialmethod

import tqdm
import transformers
from tqdm import tqdm


def silence_logging(level: int = 5):
    """Silence logging completely."""
    level = _valid_level(level)
    logging.disable(10 * level)


def silence_tensorflow(level: int = 5):
    """Silence logging from `tensorflow`."""
    level = _valid_level(level)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = str(level)


def silence_tqdm(level: int = 5):
    """Silence progress bars from `tqdm`."""
    level = _valid_level(level)
    tqdm.__init__ = partialmethod(tqdm.__init__, disable=(level > 2))


def silence_transformers(level: int = 5):
    """Silence logging from `transformers`."""
    level = _valid_level(level)
    transformers.logging.set_verbosity(10 * level)


def silence_warnings(level: int = 5):
    """Silence warnings completely except from `monapipe`."""
    level = _valid_level(level)
    actions = ["error", "always", "default", "module", "once", "ignore"]
    warnings.filterwarnings(action=actions[level], module=r"^(?!.*monapipe).*$")


def _valid_level(level: int) -> int:
    """Transform a number into a valid silence level.

    Args:
        level: The level, should be a number in ...
            - 0, 1, 2, 3, 4, 5 ("TF_CPP_MIN_LOG_LEVEL" levels)
            - 0, 10, 20, 30, 40, 50 (`logging` categories)

    Returns:
        A valid level number in 0, 1, 2, 3, 4, 5.
            0: log all messages
            1: log all messages.
            2: log all messages except DEBUG.
            3: log all messages except DEBUG and INFO.
            4: log all messages except DEBUG, INFO and WARNING.
            5: log all messages except DEBUG, INFO, WARNING and ERROR.

    """
    level = max(0, level)
    if level % 10 == 0:
        level = int(level / 10)
    level = min(level, 5)
    return level

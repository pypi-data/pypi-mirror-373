# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os

from germanetpy.germanet import Germanet

from monapipe.config import LOCAL_PATHS
from monapipe.resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> Germanet:
    """Loading method of the `germanet` resource.

    Returns:
        Germanet API.

    """
    data_path = os.path.join(LOCAL_PATHS["germanet"], "GN_V150", "GN_V150_XML")
    germanet = Germanet(data_path)
    return germanet

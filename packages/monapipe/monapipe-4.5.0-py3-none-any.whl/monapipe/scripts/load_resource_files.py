# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import sys

import monapipe.resource_handler as resources

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        path = os.path.join(os.path.dirname(__file__), "..", "resources")
        if args[1] == "all":
            names = os.listdir(path)
        else:
            names = [args[1]]
        for name in names:
            path_name = os.path.join(path, name)
            if os.path.isdir(path_name) and "load.py" in os.listdir(path_name):
                print("Loading", name, "...")
                resources.get_resource_handler(name).download()

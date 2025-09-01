# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import shutil
import sys

from monapipe.config import LOCAL_PATHS

if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        path = LOCAL_PATHS["data_path"]
        if args[1] == "all":
            names = os.listdir(path)
        else:
            names = [args[1]]
        for name in names:
            path_name = os.path.join(path, name)
            if os.path.isdir(path_name):
                print("Deleting", name, "...")
                shutil.rmtree(path_name)

# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import os
import shutil

import nltk
from nltk.corpus.util import LazyCorpusLoader

from monapipe.resource_handler import ResourceHandler

RESOURCE_PATH = os.path.dirname(__file__)

RESOURCE_HANDLER = ResourceHandler(RESOURCE_PATH)


def load() -> LazyCorpusLoader:
    """Loading method of the `open_multi_lingual_wordnet` resource.

    Returns:
        Wordnet API.

    """
    # Add new NLTK data path at `open_multilingual_wordnet/nltk_data`.
    nltk_data_path = os.path.join(RESOURCE_HANDLER.data_path, "nltk_data")
    nltk.data.path.append(nltk_data_path)
    if not os.path.exists(nltk_data_path):
        os.mkdir(nltk_data_path)

    # Download and unzip "wordnet" resource from NLTK.
    if not os.path.exists(os.path.join(nltk_data_path, "corpora", "wordnet")):
        nltk.download("wordnet", download_dir=nltk_data_path)
        shutil.unpack_archive(
            os.path.join(nltk_data_path, "corpora", "wordnet.zip"),
            os.path.join(nltk_data_path, "corpora"),
        )

    for omw in ["omw", "omw-1.4"]:
        # Download and unzip "omw" resource from NLTK;
        # download both "omw" (for older NLTK versions)
        # and "omw-1.4" (for newer NLTK versions).
        if not os.path.exists(os.path.join(nltk_data_path, "corpora", omw)):
            nltk.download(omw, download_dir=nltk_data_path)
            shutil.unpack_archive(
                os.path.join(nltk_data_path, "corpora", omw + ".zip"),
                os.path.join(nltk_data_path, "corpora"),
            )

        # Copy the German OMW file to NLTK's "omw".
        if not os.path.exists(
            os.path.join(nltk_data_path, "corpora", omw, "deu", "wn-data-deu.tab")
        ):
            os.makedirs(os.path.join(nltk_data_path, "corpora", omw, "deu"), exist_ok=True)
            shutil.copyfile(
                os.path.join(RESOURCE_HANDLER.data_path, "data", "wikt", "wn-wikt-deu.tab"),
                os.path.join(nltk_data_path, "corpora", omw, "deu", "wn-data-deu.tab"),
            )

    # Return the imported Wordnet API.
    return nltk.corpus.wordnet

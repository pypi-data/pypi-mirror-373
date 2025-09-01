# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0


def is_config(python3=True):
    return True


def unicode(x):
    return str(x)


# This file contains methods from: https://github.com/huggingface/neuralcoref/blob/master/neuralcoref/neuralcoref.pyx
# Note: It is not possible to directly import from `neuralcoref` because `neuralcoref` is incompatible with spacy v3.


def get_resolved(doc, clusters):
    """Return a list of utterrances text where the coref are resolved to the most representative mention."""
    resolved = list(tok.text_with_ws for tok in doc)
    for cluster in clusters:
        for coref in cluster:
            if coref != cluster.main:
                resolved[coref.start] = cluster.main.text + doc[coref.end - 1].whitespace_
                for i in range(coref.start + 1, coref.end):
                    resolved[i] = ""
    return "".join(resolved)


class Cluster:
    """A utility class to store our annotations in the spaCy Doc"""

    def __init__(self, i, main, mentions):
        self.i = i
        self.main = main  # A Spacy Span: main mention of the cluster
        self.mentions = mentions  # A list of Spacy Spans: list of all mentions in the cluster

    def __getitem__(self, i):
        return self.mentions[i]

    def __iter__(self):
        for mention in self.mentions:
            yield mention

    def __len__(self):
        return len(self.mentions)

    def __unicode__(self):
        return unicode(self.main) + ": " + unicode(self.mentions)

    def __bytes__(self):
        return unicode(self).encode("utf-8")

    def __str__(self):
        if is_config(python3=True):
            return self.__unicode__()
        return self.__bytes__()

    def __repr__(self):
        return self.__str__()

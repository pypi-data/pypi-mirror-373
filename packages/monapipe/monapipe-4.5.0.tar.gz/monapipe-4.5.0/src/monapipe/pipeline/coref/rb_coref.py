# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import signal
from typing import Any, Callable, List, Set

from nltk.corpus.util import LazyCorpusLoader
from spacy.language import Language
from spacy.tokens import Doc, Span

import monapipe.resource_handler as resources
from monapipe.linguistics import (
    agreement,
    get_head_nouns,
    get_morph_feat,
    get_noun_phrases,
    is_direct_speech,
    is_pronoun,
    is_proper_noun,
    longest_common_prefix,
    stringify,
)
from monapipe.neuralcoref import Cluster, get_resolved
from monapipe.pipeline.coref.coref import Coref
from monapipe.pipeline.methods import requires


@Language.factory(
    "rb_coref",
    assigns=Coref.assigns,
    default_config={},
)
def rb_coref(nlp: Language, name: str) -> Any:
    """Spacy component implementation.
        Adds coreference clusters to the document.
        Re-implementation of the algorithm presented in Krug et al. (2015):
        "Rule-based Coreference Resolution in German Historic Novels".
        Works both for UD and TIGER relations.

    Args:
        nlp: Spacy object.
        name: Component name.

    Returns:
        `RbCoref`.

    """
    return RbCoref(nlp)


class RbCoref(Coref):
    """The class `RbCoref`."""

    def __init__(self, nlp: Language):
        requires(self, nlp, ["parser", "morphologizer", "lemmatizer", "speaker_extractor"])

        super().__init__(nlp)

    def __call__(self, doc: Doc) -> Doc:
        ents = get_noun_phrases(doc)

        synonyms = [None] * len(ents)  # set of synonyms for each entity
        # (initialised with None and only computed if needed in pass 8)
        wordnet = resources.access("open_multilingual_wordnet")

        # compute the clusters
        clusters = []
        lookahead = []
        for i, ent in enumerate(ents):
            is_pron = is_pronoun(ent)

            # check whether the current entity is an indefinite, interrogative or expletive pronoun;
            # these should be excluded from coreference resolution:
            if is_pron and (
                len(
                    set(ent.root.morph.get("PronType")).intersection(
                        set(["Ind", "Int", "Neg", "Tot"])
                    )
                )
                > 0
                or (ent.root.lower_ == "es" and ent.root.dep_.split(":")[0] in ["expl", "ep"])
            ):
                continue

            # check whether current entity covers the end of the last entity
            # (happens sometimes if entities from doc.ents and doc.noun_chunks overlap);
            # if so, ignore the current (i.e. shorter) entity:
            if len(clusters) > 0 and ent.end == ents[clusters[0][0]].end:
                continue

            # for each entity, go through all passes until a cluster is found
            # (some passes are only for pronouns, others only for nouns):
            if (not is_pron) and self._pass_1_exact_match(ents, i, clusters):
                continue
            if (not is_pron) and self._pass_2_nameflexion(ents, i, clusters):
                continue
            if (not is_pron) and self._pass_3_attributes(ents, i, clusters):
                continue
            if (
                is_pron or ent.root.dep_.split(":")[0] in ["appos", "app"]
            ) and self._pass_4_precise_constructs(ents, i, clusters):
                continue
            if (not is_pron) and self._pass_5_strict_head_match(ents, i, clusters):
                continue
            if (not is_pron) and self._pass_6_relaxed_head_match(ents, i, clusters):
                continue
            if (not is_pron) and self._pass_7_title_match(ents, i, clusters):
                continue
            if (not is_pron) and self._pass_8_semantic_pass(ents, i, clusters, synonyms, wordnet):
                continue
            if is_pron and self._pass_9_pronoun_resolution(ents, i, clusters):
                continue
            if is_pron and self._pass_10_detection_of_the_addressed_person_in_direct_speech(
                ents, i, clusters
            ):
                continue
            if is_pron and self._pass_11_pronouns_in_direct_speech(ents, i, clusters):
                continue

            # if the entity appears within direct speech, it might be the case that speaker and addressee are mentioned
            # after the entity and have not been seen, yet; we push the entity on a lookahead list and try to cluster it
            # after we went through all entities:
            if (
                is_pron
                and is_direct_speech(ent)
                and ("1" in ent.root.morph.get("Person") or "2" in ent.root.morph.get("Person"))
            ):
                lookahead.append(i)
                continue

            # if no cluster is found, the entity gets a new cluster:
            clusters.insert(0, [i])

        # do pass 11 again with the lookahead entities
        for i in lookahead:
            if self._pass_11_pronouns_in_direct_speech(ents, i, clusters):
                continue

            # if no cluster is found, the entity gets a new cluster:
            clusters.insert(0, [i])

        # re-sort the order of clusters and entities
        clusters = sorted(clusters, key=lambda cluster: cluster[-1])
        clusters = [
            Cluster(i, ents[cluster[-1]], [ents[j] for j in reversed(cluster)])
            for i, cluster in enumerate(clusters)
        ]

        self._fill_doc_with_coref_clusters(doc, clusters)

        return doc

    def _alarm_handler(self, signum, frame):
        """Alarm handler for function `pass_container`."""
        raise TimeoutError()

    def _fill_doc_with_coref_clusters(self, doc: Doc, clusters: List[Cluster]):
        """Adds coreference clusters to a document.

        Args:
            doc: The document.
            clusters: All coref clusters of mentions in the document.

        """
        # initialise Token-level cluster lists
        for token in doc:
            token._.coref_clusters = []

        # fill Doc, Span, Token properties
        doc._.has_coref = True
        doc._.coref_clusters = clusters
        doc._.coref_resolved = get_resolved(doc, clusters)
        for cluster in clusters:
            for mention in cluster.mentions:
                mention._.is_coref = True
                mention._.coref_cluster = cluster
                for token in mention:
                    token._.in_coref = True
                    if cluster not in token._.coref_clusters:
                        token._.coref_clusters.append(cluster)

    def _get_synonyms(self, lemma: str, wordnet: LazyCorpusLoader) -> Set[str]:
        """Get all synonyms of a lemma from the German WordNet.

        Args:
            lemma: A lemma.
            wordnet: Wordnet API.

        Returns:
            Set of synonyms.

        """
        return set(
            [
                lemma
                for synset in wordnet.synsets(lemma, lang="deu")
                for lemma in synset.lemma_names("deu")
            ]
        )

    def _head_match_cond(
        self, ents: List[Span], cluster: List[int], index: int, strict: bool, pos_: str
    ) -> bool:
        """Checks whether the current entity should be merged with a cluster.
            Used for passes 5, 6 and 7.

        Args:
            ents: List of all entities in the document.
            cluster: List of indices of entities.
            index: Index of current entity.
            strict: Exact word match or substring match.
            pos_: POS tag of entitiy's head (should be "PROPN" or "NOUN").

        Returns:
            True iff the entity has a head match with one of the entities in the cluster.

        """
        ent1 = ents[index]
        if is_proper_noun(ent1) or pos_ == "NOUN":
            _, nouns1, propns1 = get_head_nouns(ent1, form="lemma_")
            words1 = propns1
            if pos_ == "NOUN":
                words1 = nouns1
            gender1 = get_morph_feat(ent1, "Gender")
            number1 = get_morph_feat(ent1, "Number")
            for i in cluster:
                ent2 = ents[i]
                if is_proper_noun(ent2):
                    _, nouns2, propns2 = get_head_nouns(ent2, form="lemma_")
                    words2 = propns2
                    if pos_ == "NOUN":
                        words2 = nouns2
                    gender2 = get_morph_feat(ent2, "Gender")
                    number2 = get_morph_feat(ent2, "Number")
                    if agreement(gender1, gender2) and agreement(number1, number2):
                        if strict:
                            if len(set(words1).intersection(set(words2))) > 0:
                                return True
                        else:
                            for word1 in words1:
                                for word2 in words2:
                                    if word1 in word2 or word2 in word1:
                                        return True
        return False

    def _iterate_over_recent_entities(
        self,
        ents: List[Span],
        index: int,
        clusters: List[List[int]],
        merge_condition: Callable[[List[Span], List[int], int], bool],
    ) -> bool:
        """Tries to find a cluster (of previous entities) for the current entity.

        Args:
            ents: List of all entities in the document.
            index: Index of the current entity.
            clusters: List of clusters. A cluster is a list of indices of entities.
                The order is all-reverse:
                    The most recently updated cluster is the first cluster in `clusters` etc.
                    The most recently added index is the first index in a cluster etc.
            merge_condition: A function taking three arguments: `ents`, `cluster`, `index`;
                and returning whether the entity with index `index` can be merged with the cluster.

        Returns:
            boolean: True iff a cluster could be found.
                Note that `index` is added to the corresponding cluster in `clusters`.

        """
        for i, j in sorted(
            [(ci, cj) for cj, cluster in enumerate(clusters) for ci in cluster],
            key=lambda c: c[0],
            reverse=True,
        ):
            if merge_condition(ents, [i], index):
                clusters[j].insert(0, index)
                clusters.insert(0, clusters.pop(j))
                return True
        return False

    def _pass_container(
        self,
        ents: List[Span],
        index: int,
        clusters: List[List[int]],
        merge_condition: Callable[[List[Span], List[int], int], bool],
        timeout: int = 2,
    ) -> bool:
        """Tries to find a cluster (of previous entities) for the current entity.
            Stops the search after `timeout` seconds.

        Args:
            ents: List of all entities in the document.
            index: Index of the current entity.
            clusters: List of clusters. A cluster is a list of indices of entities.
                The order is all-reverse:
                    The most recently updated cluster is the first cluster in `clusters` etc.
                    The most recently added index is the first index in a cluster etc.
            merge_condition: A function taking three arguments: `ents`, `cluster`, `index`;
                and returning whether the entity with index `index` can be merged with the cluster.
            timeout: Time in seconds after which this function is terminated.

        Returns:
            boolean: True iff a cluster could be found.
                Note that `index` is added to the corresponding cluster in `clusters`.

        """
        signal.signal(signal.SIGALRM, self._alarm_handler)
        signal.alarm(timeout)
        try:
            cluster_found = self._iterate_over_recent_entities(
                ents, index, clusters, merge_condition
            )
        except TimeoutError:
            cluster_found = False
        signal.alarm(0)
        return cluster_found

    def _pass_1_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        for i in cluster:
            ent2 = ents[i]
            if (is_proper_noun(ent1) or is_proper_noun(ent2)) and stringify(ent1) == stringify(
                ent2
            ):
                return True
        return False

    def _pass_1_exact_match(self, ents: List[Span], index: int, clusters: List[List[int]]) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_1_cond)

    def _pass_2_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        text1 = stringify(ent1)
        for i in cluster:
            ent2 = ents[i]
            text2 = stringify(ent2)
            prefix_length = len(longest_common_prefix(text1, text2))
            suffixes = ["en", "chen", "lein", "i"]
            if (
                prefix_length > 1
                and (is_proper_noun(ent1) or is_proper_noun(ent2))
                and (text1[prefix_length:] in suffixes or text2[prefix_length:] in suffixes)
            ):
                return True
        return False

    def _pass_2_nameflexion(self, ents: List[Span], index: int, clusters: List[List[int]]) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_2_cond)

    def _pass_3_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        for form in ["text", "lemma_"]:
            adjs1, nouns1, propns1 = get_head_nouns(ent1, form=form)
            text1 = " ".join(adjs1 + nouns1 + propns1)
            if text1 != "":
                gender1 = get_morph_feat(ent1, "Gender")
                number1 = get_morph_feat(ent1, "Number")
                for i in cluster:
                    ent2 = ents[i]
                    adjs2, nouns2, propns2 = get_head_nouns(ent2, form=form)
                    text2 = " ".join(adjs2 + nouns2 + propns2)
                    if text2 != "" and len(adjs1 + adjs2) > 0:
                        gender2 = get_morph_feat(ent2, "Gender")
                        number2 = get_morph_feat(ent2, "Number")
                        if (
                            agreement(gender1, gender2)
                            and agreement(number1, number2)
                            and (text1.startswith(text2 + " ") or text2.startswith(text1 + " "))
                        ):
                            return True
        return False

    def _pass_3_attributes(self, ents: List[Span], index: int, clusters: List[List[int]]) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_3_cond)

    def _pass_4_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        for i in cluster:
            ent2 = ents[i]
            if ent1.root.dep_.split(":")[0] in ["appos", "app"]:
                return ent1.root.head.i == ent2.root.i
            elif is_pronoun(ent1) and ent1.root.sent == ent2.root.sent:
                match = False
                morph = ent2.root.morph
                if (
                    ent1.root.head.dep_.split(":")[0] in ["acl", "rc"]
                    and [
                        tok for tok in ent1.root.head.children if not (tok.is_punct or tok.is_space)
                    ][0].i
                    == ent1.root.i
                ):
                    if agreement(ent1.root.morph.get("Person"), morph.get("Person")) and agreement(
                        ent1.root.morph.get("Number"), morph.get("Number")
                    ):
                        match = True
                elif ent1.root.lower_ in ["mich", "dich", "sich", "uns", "euch"]:
                    if (
                        (
                            ent1.root.lower_ == "mich"
                            and "1" in morph.get("Person")
                            and "Sing" in morph.get("Number")
                        )
                        or (
                            ent1.root.lower_ == "dich"
                            and "2" in morph.get("Person")
                            and "Sing" in morph.get("Number")
                        )
                        or (
                            ent1.root.lower_ == "uns"
                            and "1" in morph.get("Person")
                            and "Plur" in morph.get("Number")
                        )
                        or (
                            ent1.root.lower_ == "euch"
                            and "2" in morph.get("Person")
                            and "Plur" in morph.get("Number")
                        )
                        or (
                            ent1.root.lower_ == "sich"
                            and "1" not in morph.get("Person")
                            and "2" not in morph.get("Person")
                        )
                    ):
                        match = True
                if match:
                    return True
        return False

    def _pass_4_precise_constructs(
        self, ents: List[Span], index: int, clusters: List[List[int]]
    ) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_4_cond)

    def _pass_5_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        return self._head_match_cond(ents, cluster, index, True, "PROPN")

    def _pass_5_strict_head_match(
        self, ents: List[Span], index: int, clusters: List[List[int]]
    ) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_5_cond)

    def _pass_6_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        return self._head_match_cond(ents, cluster, index, False, "PROPN")

    def _pass_6_relaxed_head_match(
        self, ents: List[Span], index: int, clusters: List[List[int]]
    ) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_6_cond)

    def _pass_7_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        return self._head_match_cond(ents, cluster, index, True, "NOUN")

    def _pass_7_title_match(self, ents: List[Span], index: int, clusters: List[List[int]]) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_7_cond)

    def _pass_8_cond(
        self,
        ents: List[Span],
        cluster: List[int],
        index: int,
        synonyms: List[List[str]],
        wordnet: LazyCorpusLoader,
    ) -> bool:
        ent1 = ents[index]
        if not is_pronoun(ent1):
            gender1 = get_morph_feat(ent1, "Gender")
            number1 = get_morph_feat(ent1, "Number")
            if synonyms[index] is None:
                _, words1, _ = get_head_nouns(ent1, form="lemma_")
                synonyms[index] = [
                    lemma for word in words1 for lemma in self._get_synonyms(word, wordnet)
                ]
            synonyms1 = set(synonyms[index])
            for i in cluster:
                ent2 = ents[i]
                if not is_pronoun(ent2):
                    gender2 = get_morph_feat(ent2, "Gender")
                    number2 = get_morph_feat(ent2, "Number")
                    if synonyms[i] is None:
                        _, words2, _ = get_head_nouns(ent2, form="lemma_")
                        synonyms[i] = [
                            lemma for word in words2 for lemma in self._get_synonyms(word, wordnet)
                        ]
                    synonyms2 = set(synonyms[i])
                    if agreement(gender1, gender2) and agreement(number1, number2):
                        if len(synonyms1.intersection(synonyms2)) > 0:
                            return True
        return False

    def _pass_8_semantic_pass(
        self,
        ents: List[Span],
        index: int,
        clusters: List[List[int]],
        synonyms: List[Set[str]],
        wordnet: LazyCorpusLoader,
    ) -> bool:
        return self._pass_container(
            ents,
            index,
            clusters,
            lambda ents, cluster, index: self._pass_8_cond(ents, cluster, index, synonyms, wordnet),
        )

    def _pass_9_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        if is_pronoun(ent1):
            gender1 = get_morph_feat(ent1, "Gender")
            number1 = get_morph_feat(ent1, "Number")
            person1 = get_morph_feat(ent1, "Person")
            direct1 = is_direct_speech(ent1)
            for i in cluster:
                ent2 = ents[i]
                subjs = [
                    ent
                    for ent in ents
                    if ent.root.sent == ent2.root.sent
                    and ent.root.dep_.split(":")[0] in ["nsubj", "sb"]
                ]
                if ent2 not in subjs:
                    subjs = [ents.index(subj) for subj in reversed(subjs)]
                    if self._pass_9_cond(ents, [j for j in subjs if j < index], index):
                        return False
                gender2 = get_morph_feat(ent2, "Gender")
                number2 = get_morph_feat(ent2, "Number")
                person2 = get_morph_feat(ent2, "Person")
                direct2 = is_direct_speech(ent2)
                if (
                    agreement(gender1, gender2)
                    and agreement(number1, number2, strict=True)
                    and agreement(person1, person2)
                    and (
                        (not direct1 and not direct2)
                        or (
                            direct1
                            and direct2
                            and ent1.root._.span["speech"] == ent2.root._.span["speech"]
                        )
                        # (either both entities are not within direct speech or both are within the same direct speech segment)
                    )
                ):
                    return True
        return False

    def _pass_9_pronoun_resolution(
        self, ents: List[Span], index: int, clusters: List[List[int]]
    ) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_9_cond)

    def _pass_10_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        direct1 = is_direct_speech(ent1)
        person1 = get_morph_feat(ent1, "Person")
        if direct1 and "2" in person1:
            number1 = get_morph_feat(ent1, "Number")
            for i in cluster:
                ent2 = ents[i]
                direct2 = is_direct_speech(ent2)
                if (
                    direct2
                    and is_proper_noun(ent2)
                    and ent1.root.sent == ent2.root.sent  # same sentence
                    and ent1.root._.span["speech"]
                    == ent2.root._.span["speech"]  # same direct speech segment
                ):
                    number2 = get_morph_feat(ent2, "Number")
                    if agreement(number1, number2, strict=True):
                        return True
        return False

    def _pass_10_detection_of_the_addressed_person_in_direct_speech(
        self, ents: List[Span], index: int, clusters: List[List[int]]
    ) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_10_cond)

    def _pass_11_cond(self, ents: List[Span], cluster: List[int], index: int) -> bool:
        ent1 = ents[index]
        if is_direct_speech(ent1):
            person1 = get_morph_feat(ent1, "Person")
            if "1" in person1 or "2" in person1:
                number1 = get_morph_feat(ent1, "Number")
                if ent1.root._.span["speech"]._.speaker in ents:
                    number2 = get_morph_feat(ent1.root._.span["speech"]._.speaker, "Number")
                    if (
                        ents.index(ent1.root._.span["speech"]._.speaker) in cluster
                        and "1" in person1
                        and agreement(number1, number2, strict=True)
                    ):
                        return True
                if ent1.root._.span["speech"]._.addressee in ents:
                    number2 = get_morph_feat(
                        ent1.root._.span["speech"]._.addressee in ents, "Number"
                    )
                    if (
                        ents.index(ent1.root._.span["speech"]._.addressee) in cluster
                        and "2" in person1
                        and agreement(number1, number2, strict=True)
                    ):
                        return True
        for i in cluster:
            if i < index and self._pass_11_cond(ents, [index], i):
                return True
        return False

    def _pass_11_pronouns_in_direct_speech(
        self, ents: List[Span], index: int, clusters: List[List[int]]
    ) -> bool:
        return self._pass_container(ents, index, clusters, self._pass_11_cond)

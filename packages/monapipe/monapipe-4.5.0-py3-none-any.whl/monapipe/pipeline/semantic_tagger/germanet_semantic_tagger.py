# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any, List, Optional, Tuple

from germanetpy.germanet import Germanet
from germanetpy.synset import Synset
from spacy.language import Language
from spacy.tokens import Doc, Span, Token

import monapipe.resource_handler as resources
from monapipe.pipeline.methods import requires
from monapipe.pipeline.semantic_tagger.semantic_tagger import SemanticTagger


@Language.factory(
    "germanet_semantic_tagger",
    assigns=SemanticTagger.assigns,
    default_config={},
)
def germanet_semantic_tagger(nlp: Language, name: str) -> Any:
    """Spacy component implementation.
        Add GermaNet synsets to adjectives, root verbs and clauses.

    Args:
        nlp: Spacy object.
        name: Component name.

    Returns:
        `GermanetSemanticTagger`.

    """
    return GermanetSemanticTagger(nlp)


class GermanetSemanticTagger(SemanticTagger):
    """The class `GermanetSemanticTagger`."""

    def __init__(self, nlp: Language):
        requires(self, nlp, ["lemmatizer", "clausizer"])

        super().__init__(nlp)

    def __call__(self, doc: Doc) -> Doc:
        germanet = resources.access("germanet")
        for clause in doc._.clauses:
            target_synset = self._verb_class_disambiguation_via_subj_obj(clause, germanet)
            if target_synset.startswith("s"):
                clause._.verb_synset_id = target_synset
                if clause.root.pos_ == "VERB":
                    clause.root._.synset_id = target_synset
            for token in clause:
                if token.pos_ == "ADJ":
                    token._.synset_id = self._adjective_class_disambiguation(token, germanet)
                if token.pos_ in ["ADJ", "VERB"] and token._.synset_id is None:
                    # If nothing of the above yields a synset ID, return a default synset ID.
                    token._.synset_id = self._get_default_synset_id(token, germanet)
        return doc

    def _add_ranking(
        self, path_sorted_synset_list: List[Tuple[Synset, Synset, int]]
    ) -> List[Tuple[Synset, Synset, int]]:
        """Ranks synsets by distance between them.

        Args:
            List with two synsets and path between them sorted by the shortest path.

        Returns:
            List with two synsets and path between them sorted by the shortes path.

        """
        shortest_dist = []
        for i, syns in enumerate(path_sorted_synset_list):
            try:
                if path_sorted_synset_list[i][2] == path_sorted_synset_list[i + 1][2]:
                    shortest_dist.append(syns)
            except:
                pass
        return shortest_dist

    def _adjective_class_disambiguation(self, token: Token, germanet: Germanet) -> Optional[str]:
        """Disambiguated tokens by the synset id.

        Args:
            token: The token.
            germanet: Germanet API.

        Returns:
            Synset id.

        """
        adjective_synsets = self._get_synsets_for_token(token, germanet)
        if adjective_synsets:
            # if the word is unambiguous and has the same meaning in all contexts
            if len(adjective_synsets) == 1:
                return adjective_synsets[0].id

            head_synsets = []
            head_of_head_synsets = []

            if len(adjective_synsets) > 1:
                # assumption that you should not disambiguate an adj with another (conjuncted) adj, but maybe it's wrong
                # if token.head.pos_ in ["ADJ", "CCONJ"]:
                # while token.head.pos_ not in ["ADJ", "CCONJ"]:
                # token = token.head
                head_synsets = self._get_synsets_for_token(token.head, germanet)
                head_of_head = self._get_synsets_for_token(token.head.head, germanet)
                if head_synsets is None:
                    while head_synsets is None:
                        token = token.head
                        if token.dep_ == "ROOT":
                            break
                    head_synsets = self._get_synsets_for_token(token.head, germanet)
                    head_of_head = self._get_synsets_for_token(token.head.head, germanet)
                # if the head is also an adective move up in the structure until
                if head_of_head is None:
                    while head_of_head is None:
                        token = token.head
                        if token.dep_ == "ROOT":
                            break
                    head_of_head = self._get_synsets_for_token(token.head.head, germanet)
                if head_of_head == head_synsets and head_of_head != None:
                    head_of_head_synsets = self._get_synsets_for_token(token.head.head, germanet)
                else:
                    head_of_head_synsets = head_of_head
                # if the token is root it can be disambiguated through the subject in the noun phrase
                if token.dep_ == "ROOT":
                    for word in token.subtree:
                        # better to disambiguate with subject np, but if it's not there copular verb will be used
                        # TODO: consider different sentence structures
                        if word.dep_ == "cop":
                            head_synsets = self._get_synsets_for_token(word, germanet)
                        if word.dep_ == "nsubj":
                            head_synsets = self._get_synsets_for_token(word, germanet)
                elif token.head.dep_ == "ROOT":
                    for word in token.subtree:
                        # disambiguate either with nsubj, if not available -> cop
                        if word.dep_ == "nsubj":
                            head_of_head_synsets = self._get_synsets_for_token(word, germanet)
                        elif word.dep_ == "cop":
                            head_of_head_synsets = self._get_synsets_for_token(word, germanet)
                # elif token.head.head.dep_ == "ROOT":
                #    head_of_head_synsets = get_synsets_for_token(token.head.head)
            distances = []
            if isinstance(head_synsets, list):
                distance = self._add_ranking(
                    self._sort_synsets_by_distance(adjective_synsets, head_synsets)
                )
                if len(distance) == 1:
                    return distance[0][0].id
                elif len(distance) > 1:
                    distances = distance

            elif isinstance(head_of_head_synsets, list) and len(distances) > 0:
                distance = self._add_ranking(
                    self._sort_synsets_by_distance(head_synsets, head_of_head_synsets)
                )
                if len(distance) == 1:
                    s_id = distance[0][0].id
                    for i in distances:
                        dist = []
                        if s_id == i[1].id:
                            dist.append(i)
                        if len(dist) == 1:
                            return i[0].id

    def _get_default_synset_id(self, token: Token, germanet: Germanet) -> Optional[str]:
        """Return the smallest synset ID for a token, if there is any.

        Args:
            token: The token.
            germanet: Germanet API.

        Returns:
            Synset id.

        """
        synsets = self._get_synsets_for_token(token, germanet)
        if synsets is not None:
            s_ids = [s.id for s in synsets if s.id.startswith("s") and s.id[1:].isnumeric()]
            if len(s_ids) > 0:
                return sorted(s_ids, key=lambda s_id: int(s_id[1:]))[0]
        return None

    def _get_synsets_for_token(self, token: Token, germanet: Germanet) -> Optional[List[Synset]]:
        """Extracts synstets for a token.

        Args:
            token: The token.
            germanet: Germanet API.

        Returns:
            list of synsets for the token.

        """
        synsets = germanet.get_synsets_by_orthform(token.lemma_)
        if len(synsets) > 0:
            return synsets
        return None

    def _sort_synsets_by_distance(
        self, synsets_list_1: List[Synset], synsets_list_2: List[Synset]
    ) -> List[Tuple[Synset, Synset, int]]:
        """Sorts synsets by distance between them

        Args:
            synsets_list_1: Synset list for first word.
            synsets_list_2: Synset list for second word.

        Returns:
            List with two synsets and path between them sorted by the shortest path.

        """
        distances_between_synsets = []
        for s_1 in synsets_list_1:
            for s_2 in synsets_list_2:
                distances_between_synsets.append((s_1, s_2, len(s_1.shortest_path(s_2)[0])))
                path_sorted_synset_list = sorted(
                    distances_between_synsets, key=lambda element: element[2], reverse=False
                )
        return path_sorted_synset_list

    def _verb_class_disambiguation_via_subj_obj(self, clause: Span, germanet: Germanet) -> str:
        """TODO

        Args:
            clause: Clause.
            germanet: Germanet API.

        Returns:
            lowest_scoring_verb_synset_id

        """
        if clause.root.pos_ == "VERB":
            verb_token = clause.root
        else:
            return "ellipsis"

        ##find synsets for verb
        verb_synsets = germanet.get_synsets_by_orthform(verb_token.lemma_)
        if len(verb_synsets) == 0:
            return "verb not in germanet"

        ##find synsets for subj and obj
        # define list for sents with multiple objects
        all_obj_synsets = list()
        for token in clause:
            if (
                token.dep_ in ["nsubj", "nsubj:pass"]
                and len(germanet.get_synsets_by_orthform(token.lemma_)) > 0
            ):
                nsubj_synsets = germanet.get_synsets_by_orthform(token.lemma_)
            if (
                token.dep_ in ["obj", "obl", "obl:agent", "obl:arg", "obl:lmod", "obl:tmod"]
                and len(germanet.get_synsets_by_orthform(token.lemma_)) > 0
            ):
                all_obj_synsets.append(germanet.get_synsets_by_orthform(token.lemma_))

        # find all path distances for each combination of subj synsets to verb synsets
        if "nsubj_synsets" in locals():
            verb_subj_distances = list()
            for verb_synset in verb_synsets:
                for nsubj_synset in nsubj_synsets:
                    verb_subj_distances.append(
                        [verb_synset, nsubj_synset, len(verb_synset.shortest_path(nsubj_synset)[0])]
                    )
            verb_subj_distances_sorted = sorted(
                verb_subj_distances, key=lambda element: element[2], reverse=False
            )

        # find all path distances for each combination of obj synsets for each obj to verb synsets
        if len(all_obj_synsets) > 0:
            all_verb_obj_distances_sorted = list()
            for obj_synsets in all_obj_synsets:
                if len(obj_synsets) > 0:
                    verb_obj_distances = list()
                    for verb_synset in verb_synsets:
                        for obj_synset in obj_synsets:
                            verb_obj_distances.append(
                                [
                                    verb_synset,
                                    obj_synset,
                                    len(verb_synset.shortest_path(obj_synset)[0]),
                                ]
                            )
                    verb_obj_distances_sorted = sorted(
                        verb_obj_distances, key=lambda element: element[2], reverse=False
                    )
                    all_verb_obj_distances_sorted.append(verb_obj_distances_sorted)

        # all_distances_sorted = all_verb_obj_distances_sorted + [verb_subj_distances_sorted]
        all_distances_sorted = list()
        if "all_verb_obj_distances_sorted" in locals():
            all_distances_sorted += all_verb_obj_distances_sorted
        if "verb_subj_distances_sorted" in locals():
            all_distances_sorted += [verb_subj_distances_sorted]
        if len(all_distances_sorted) == 0:
            return "no subj and obj or no germanet synsets for it."
        # RANKING
        # ranks the smallest distances for each verb-subj or verb-obj from 1 to 3
        # if distances equal each other the rank is give twice/multiple times
        all_distances_sorted_ranks = list()
        for distances_sorted in all_distances_sorted:
            rank = 1
            distances_sorted_ranks = list()
            for distance_sorted_i, _ in enumerate(distances_sorted):
                try:
                    synset = distances_sorted[distance_sorted_i]
                    synset.append(rank)
                    distances_sorted_ranks.append(synset)
                    if (
                        distances_sorted[distance_sorted_i][2]
                        != distances_sorted[distance_sorted_i + 1][2]
                    ):
                        rank += 1
                except:
                    continue
            all_distances_sorted_ranks.append(distances_sorted_ranks)

        # SCORING VERB CATEGORY
        # builds a ordered list for verb synsets that have at least one time an rank between 1 and 3
        verb_synset_dic = dict()
        for distances_sorted_ranks in all_distances_sorted_ranks:
            for distances_sorted_rank in distances_sorted_ranks:
                verb_synset = distances_sorted_rank[0]
                rank = distances_sorted_rank[3]
                if verb_synset.id not in verb_synset_dic:
                    verb_synset_dic[verb_synset.id] = rank
                else:
                    verb_synset_dic[verb_synset.id] += rank
        verb_synset_dic_sorted = sorted(
            verb_synset_dic.items(), key=lambda element: element[1], reverse=False
        )

        # the lowest score is assumed as the assigned synset to the verb
        lowest_scoring_verb_synset_id = verb_synset_dic_sorted[0][0]

        # returns the synset id for lowest verb score
        return lowest_scoring_verb_synset_id

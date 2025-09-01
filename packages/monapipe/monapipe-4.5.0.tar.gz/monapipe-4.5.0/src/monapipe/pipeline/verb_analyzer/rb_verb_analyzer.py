# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import itertools
import json
from typing import Any, Dict, List, Set, Tuple

import more_itertools
from spacy.language import Language
from spacy.tokens import Doc, MorphAnalysis, Span, Token

from monapipe.linguistics import get_morph_analyses
from monapipe.lookups import lookup
from monapipe.pipeline.methods import requires
from monapipe.pipeline.verb_analyzer.verb_analyzer import VerbAnalyzer


@Language.factory(
    "rb_verb_analyzer",
    assigns=VerbAnalyzer.assigns,
    default_config={
        "ov": True,
        "conj_rule_labels": ["conj"],
        "handle_semi_modals": True,
        "handle_particles": True,
        "handle_substitute_infinitives": True,
        "handle_local_verb_movement": True,
    },
)
def rb_verb_analyzer(
    nlp: Language,
    name: str,
    ov: bool,
    conj_rule_labels: List[str],
    handle_semi_modals: bool,
    handle_particles: bool,
    handle_substitute_infinitives: bool,
    handle_local_verb_movement: bool,
) -> Any:
    """Spacy component implementation.
        Add morpho-syntactic analyses of compound verbs.
        This implementation combines different previous versions that can be found here:
            - https://gitlab.gwdg.de/mona/pipy-public/-/blob/main/pipeline/components/tense_tagger.py
            - https://gitlab.gwdg.de/tillmann.doenicke/disrpt2021-tmvm/-/blob/master/extract_features.py
            - https://gitlab.gwdg.de/tillmann.doenicke/mrl2022-tmvm/-/blob/master/grammatical_analysis.py

    Args:
        nlp: Spacy object.
        name: Component name.
        ov: True if the language has OV word order (e.g. German); False if the language has VO word order (e.g. English).
        conj_rule_labels: Dependency relations that qualify as root nodes of conjunctional clauses.
        handle_semi_modals: False iff semi-modal verbs should always be treated as full verbs.
            Otherwise, they are treated as full verbs or modal verbs depending on context.
        handle_particles: True iff morphological features from verbal particles should be copied to their head verbs.
        handle_substitute_infinitives: True iff infinitive verbs governed by perfect auxiliaries should be
            analyzed as past perfect participles (so-called "substitute infinitives", e.g. in German).
        handle_local_verb_movement: False iff the word order within a compound verb should be taken to be fixed.
            Otherwise, the order is taken to be flexible (and more compound verb analyses are possible).

    Returns:
        `RbVerbAnalyzer`.

    """
    return RbVerbAnalyzer(
        nlp,
        ov,
        conj_rule_labels,
        handle_semi_modals,
        handle_particles,
        handle_substitute_infinitives,
        handle_local_verb_movement,
    )


class RbVerbAnalyzer(VerbAnalyzer):
    """The class `RbVerbAnalyzer`."""

    def __init__(
        self,
        nlp: Language,
        ov: bool,
        conj_rule_labels: List[str],
        handle_semi_modals: bool,
        handle_particles: bool,
        handle_substitute_infinitives: bool,
        handle_local_verb_movement: bool,
    ):
        requires(self, nlp, ["morphologizer", "lemmatizer", "clausizer"])

        super().__init__(
            nlp,
            ov,
            conj_rule_labels,
            handle_semi_modals,
            handle_particles,
            handle_substitute_infinitives,
            handle_local_verb_movement,
        )

    def __call__(self, doc: Doc) -> Doc:
        # read language-specific inflection table, auxiliary verbs and modal verbs
        inflection_table = lookup(doc.lang_, "inflection_table")
        auxiliary_verbs = lookup(doc.lang_, "auxiliary_verbs")
        auxiliary_verbs = {
            aux: set(aux_lemmas.split("|")) for aux, aux_lemmas in auxiliary_verbs.items()
        }
        aux_lemmas = set().union(*auxiliary_verbs.values())
        mod_lemmas = lookup(doc.lang_, "modal_verbs")
        if self.handle_semi_modals:
            mod_lemmas = mod_lemmas.union(lookup(doc.lang_, "semi_modal_verbs"))

        for clause in doc._.clauses:
            # perform grammatical analysis
            _, analysis, verbs, main_verb, modal_verbs = self._compute_verb_analysis(
                clause, aux_lemmas, mod_lemmas, inflection_table, auxiliary_verbs
            )

            clause._.form = MorphAnalysis(doc.vocab, analysis)
            clause._.form_verbs = verbs
            clause._.form_main = main_verb
            clause._.form_modals = modal_verbs

        return doc

    def _apply_conjunct_rules(
        self, verbs: List[Tuple[Token, Dict[str, str]]], clause: Span
    ) -> List[Tuple[Token, Dict[str, str]]]:
        """If the current clause is a conjunct,
            copy verbs from the matrix clause.

        Args:
            verbs: List of (verb, analysis) tuples.
            clause: The corresponding clause.

        Returns:
            Updated list of (verbs, analysis) tuples.

        """
        if clause.root.dep_ in self.conj_rule_labels:
            prec_clause = clause.root.head._.clause
            if prec_clause is not None:
                prec_verbs = prec_clause._.form_verbs  # these are the verbs from the matrix clause
                prec_verbs = [(verb, verb.morph.to_dict()) for verb in prec_verbs]
                if not self.ov:
                    prec_verbs = list(reversed(prec_verbs))
                if len(verbs) == 0:
                    # if there are no verbs in the conjunct, we copy all verbs from the matrix clause
                    verbs.extend(prec_verbs)
                elif len(prec_verbs) > 0:
                    # otherwise, we copy the missing succeeding and preceding verbs
                    s_verbs = [
                        verb
                        for verb in prec_verbs[:-1]
                        if self._doc_i(verb) > self._doc_i(verbs[-1])
                    ]
                    p_verbs = [
                        verb
                        for verb in prec_verbs[:-1]
                        if self._doc_i(verb) < self._doc_i(verbs[0])
                    ]
                    # the finite verb of the matrix clause has to go to the end (as for the conjunct)
                    _, last_prec_verb_analysis = prec_verbs[-1]
                    if (
                        self._doc_i(prec_verbs[-1]) > self._doc_i(verbs[-1])
                        or last_prec_verb_analysis.get("VerbForm") == "Fin"
                    ):
                        s_verbs.append(prec_verbs[-1])
                    else:
                        p_verbs.append(prec_verbs[-1])
                    _, last_verb_analysis = verbs[-1]
                    if last_verb_analysis.get("VerbForm") != "Fin":
                        # 1) the conjunct has no finite verb:
                        #    we might have to copy syntactically high verbs from the matrix clause,
                        #      "[dass Hans Maria gesehen [und gerufen] hat]"
                        #      -> gesehen hat; gerufen hat
                        for i in range(0, len(s_verbs) + 1):
                            s_verb_analysis = {}
                            if i < len(s_verbs):
                                _, s_verb_analysis = s_verbs[-(i + 1)]
                            if i == len(s_verbs) or last_verb_analysis.get(
                                "VerbForm"
                            ) == s_verb_analysis.get("VerbForm"):
                                verbs.extend(s_verbs[len(s_verbs) - i :])
                                break
                    # 2) we might have to copy syntactically low verbs from the matrix clause,
                    #      "[dass Hans Maria gesehen hat] [und hatte]"
                    #      -> gesehen hat; gesehen hatte
                    _, first_verb_analysis = verbs[0]
                    for i in range(0, len(p_verbs) + 1):
                        p_verb_analysis = {}
                        if i < len(p_verbs):
                            _, p_verb_analysis = p_verbs[i]
                        if i == len(p_verbs) or first_verb_analysis.get(
                            "VerbForm"
                        ) == p_verb_analysis.get("VerbForm"):
                            verbs = p_verbs[:i] + verbs
                            break
        return verbs

    def _apply_particle_rule(
        self, tokens: List[Tuple[Token, Dict[str, str]]]
    ) -> List[Tuple[Token, Dict[str, str]]]:
        """Copy features from particles to their heads;
            remove particles afterwards.

        Args:
            tokens: List of (token, analysis) tuples.

        Returns:
            Updated list of (verbs, analysis) tuples.

        """
        if self.handle_particles:
            for token, token_analysis in tokens:
                if token.pos_ == "PART":
                    for verb, verb_analysis in tokens:
                        if verb == token.head:
                            verb_analysis.update(token_analysis)
                            break
            return [
                (token, token_analysis)
                for token, token_analysis in tokens
                if token.pos_ in ["AUX", "VERB"]
            ]

    def _apply_substitute_infinitive_rule(
        self, verbs: List[Tuple[Token, Dict[str, str]]], auxiliary_verbs: Dict[str, Set[str]]
    ) -> List[Tuple[Token, Dict[str, str]]]:
        """If an infinitive verb is governed by a perfect auxiliary ("AUX1"),
            change the verb's analysis to a past perfect participle analysis.

        Args:
            verbs: List of (verb, analysis) tuples.
            auxiliary_verbs: Lemmas of auxiliary verbs grouped by auxiliary verb category.

        Returns:
            Updated list of (verb, analysis) tuples.

        """
        if self.handle_substitute_infinitives:
            if len(verbs) > 1:
                last_verb, _ = verbs[-1]
                _, prec_verb_analysis = verbs[-2]
                if (
                    last_verb.lemma_ in auxiliary_verbs["AUX1"]
                    and prec_verb_analysis.get("VerbForm") == "Inf"
                ):
                    prec_verb_category = prec_verb_analysis["Category"]
                    prec_verb_analysis.clear()
                    prec_verb_analysis.update(
                        {"VerbForm": "Part", "Aspect": "Perf", "Tense": "Past"}
                    )
                    prec_verb_analysis["Category"] = prec_verb_category
        return verbs

    def _clone_analyses(self, obj: Any) -> Any:
        """Clone a structure that contains analyses dictionaries,
            so that the analyses can be altered in the cloned copy without changing the originals.

        Args:
            obj: A nested structure containing lists, tuples and dictionaries.

        Returns:
            A copy of it where all lists, tuples and dictionaries have been cloned.

        """
        if isinstance(obj, (tuple, list)):
            type_ = type(obj)
            return type_([self._clone_analyses(elem) for elem in obj])
        elif isinstance(obj, dict):
            return {key: self._clone_analyses(val) for key, val in obj.items()}
        return obj

    def _combine_analyses(
        self, analyses: List[Tuple[Dict[str, str], List[Token]]]
    ) -> Tuple[Dict[str, str], List[Token]]:
        """Combine multiple analyses into one.
            The combined analysis contains those features,
            for which all remaining analyses have a common value.

        Args:
            List of (analysis, verbs) tuples.

        Returns:
            The (combined analysis, verbs) tuple.

        """
        combined_analysis = {}
        combined_verbs = []
        for analysis, verbs in analyses:
            for feat in analysis:
                vals = set(analysis[feat].split(","))
                try:
                    combined_analysis[feat].intersection_update(vals)
                except KeyError:
                    combined_analysis[feat] = vals
            if len(verbs) > len(combined_verbs):
                combined_verbs = verbs
        combined_analysis = {
            feat: ",".join(list(combined_analysis[feat]))
            for feat in combined_analysis
            if len(combined_analysis[feat]) > 0
        }
        return combined_analysis, combined_verbs

    def _compute_verb_analysis(
        self,
        clause: Span,
        aux_lemmas: Set[str],
        mod_lemmas: Set[str],
        inflection_table: List[Tuple[List[Dict[str, str]], Dict[str, str]]],
        auxiliary_verbs: Dict[str, Set[str]],
    ) -> Tuple[Dict[str, str], List[Token], Token, List[Token]]:
        """Compute the grammatical features of a clause.

        Args:
            clause: The clause.
            aux_lemmas: Lemmas of auxiliary verbs.
            mod_lemmas: Lemmas of modal verbs.
            inflection_table: Complete inflection table.
            auxiliary_verbs: Lemmas of auxiliary verbs grouped by auxiliary verb category.

        Returns:
            All possible features of the compound verb in the clause.
                If the compound verb is unambiguous, the list contains only one argument,
                which is identical to the second return value.
            The features of the compound verb in the clause.
            The words that belong to the compound verb.
            The main verb.
            The modal verbs.

        """
        # Get the tokens of the compound verb.
        compound_verb = self._get_compound_verb(clause)

        # Get the morphological analyses for each token.
        compound_verb = [
            [(token, token_analysis) for token_analysis in get_morph_analyses(token)]
            for token in compound_verb
        ]

        # Construct all possible combinations of morphological analyses.
        compound_verbs = self._clone_analyses(itertools.product(*compound_verb))

        # The algorithm removes tokens from the construction in various places,
        # resulting in analyses for constructions of different length.
        # We therefore save the analyses in this dictionary, sorted by length.
        compound_analyses = {}  # length of the construction : list of analyses

        for compound_verb in compound_verbs:
            # Copy the features from particles to their head verbs; remove all particles afterwards.
            compound_verb = self._apply_particle_rule(compound_verb)

            # Bring the verbs in the order of an OV language;
            # basically: from syntactically lowest to syntactically highest.
            if not self.ov:
                compound_verb = list(reversed(compound_verb))

            # Some verbs are underspecified w.r.t. "VerbForm" (finite/infinite);
            # loop over finite/infinite analyses for these unanalyzed verbs.
            unknown_verbs = [
                verb for verb, verb_analysis in compound_verb if "VerbForm" not in verb_analysis
            ]
            unknown_verbs_ = self._clone_analyses(more_itertools.powerset(unknown_verbs))
            for unknown_verbs in unknown_verbs_:
                finite_verbs = [
                    (verb, verb_analysis)
                    for verb, verb_analysis in compound_verb
                    if verb_analysis.get("VerbForm") == "Fin" or verb in unknown_verbs
                ]  # the finite verbs and the underspecified verbs
                infinite_verbs = [
                    verb for verb in compound_verb if verb not in finite_verbs
                ]  # the other verbs

                # Select the syntactically highest finite verb;
                # remove all other finite verbs.
                if len(finite_verbs) > 1:
                    finite_verbs = [finite_verbs[-1]]

                # Counteract finite-verb movement (affects e.g. V2 languages).
                verbs = infinite_verbs + finite_verbs

                # If the clause is a conjunct, it is necessary to copy the missing verbs from the matrix clause
                # (the preceding conjunct).
                verbs = self._apply_conjunct_rules(verbs, clause)

                if len(verbs) > 0:
                    # Separate the verbs into auxiliaries, modals and main verbs;
                    # select the syntactically highest main verb;
                    # cut off all lower verbs.
                    main_verbs = []
                    for verb, verb_analysis in verbs:
                        if verb.lemma_ in aux_lemmas:
                            verb_analysis["Category"] = "Aux"
                        elif verb.lemma_ in mod_lemmas:
                            verb_analysis["Category"] = "Mod"
                        else:
                            verb_analysis["Category"] = "Main"
                            main_verbs.append((verb, verb_analysis))
                    if len(main_verbs) == 0:
                        verb, verb_analysis = verbs[0]
                        verb_analysis["Category"] = "Main"
                        main_verbs.append((verb, verb_analysis))
                    verbs = verbs[verbs.index(main_verbs[-1]) :]

                    # Change the analysis of substitute infinitives to a past perfect participle analysis.
                    verbs = self._apply_substitute_infinitive_rule(verbs, auxiliary_verbs)

                    # Shift the features of modal verbs to syntactically lower position.
                    for i in reversed(range(1, len(verbs))):
                        _, modal_verb_analysis = verbs[i]
                        if modal_verb_analysis["Category"] == "Mod":
                            _, verb_analysis = verbs[i - 1]
                            verb_category = verb_analysis["Category"]
                            verb_analysis.clear()
                            verb_analysis.update(modal_verb_analysis)
                            verb_analysis["Category"] = verb_category

                    # Shift the main verb rightwards until an analysis is found.
                    while len(verbs) > 0:
                        _, main_verb_analysis = verbs[0]
                        main_verb_analysis["Category"] = "Main"

                        # Exclude modal verbs.
                        verbs_combination = []
                        for verb, verb_analysis in verbs:
                            if verb_analysis["Category"] != "Mod":
                                verbs_combination.append((verb, verb_analysis))
                        verbs_combinations = [verbs_combination]

                        # Map morphological features to grammatical features.
                        analyses = set()
                        for verbs_combination in verbs_combinations:
                            analyses.update(self._lookup(verbs_combination, inflection_table))
                        analyses = [json.loads(analysis) for analysis in analyses]

                        # If no analysis is found and only one verb is left,
                        # treat the verb as simple form.
                        if len(analyses) == 0 and len(verbs) == 1:
                            analyses = [
                                {
                                    feat: val
                                    for feat, val in verb_analysis.items()
                                    if feat in ["Aspect", "Tense", "Mood", "VerbForm", "Voice"]
                                }
                                for verb_combination in verbs_combinations
                                for _, verb_analysis in verb_combination
                            ]

                        analyses = [(analysis, verbs) for analysis in analyses]
                        if len(analyses) > 0:
                            try:
                                compound_analyses[len(verbs)].extend(analyses)
                            except KeyError:
                                compound_analyses[len(verbs)] = analyses
                            break

                        verbs = verbs[1:]

        if len(compound_analyses) == 0:
            return [], {}, [], None, []

        else:
            analyses = compound_analyses[max(compound_analyses.keys())]
            analyses = self._filter_analyses(analyses)

            # Combine the remaining analyses into one.
            final_analysis, final_verbs = self._combine_analyses(analyses)

            # Get main verb, modal verbs and all verbs.
            final_main_verb, _ = final_verbs[0]
            final_modal_verbs = [
                verb for verb, verb_analysis in final_verbs if verb_analysis["Category"] == "Mod"
            ]
            final_verbs = [verb for verb, _ in final_verbs]

            if not self.ov:
                # Restore the original word order.
                final_verbs = list(reversed(final_verbs))
                final_modal_verbs = list(reversed(final_modal_verbs))

            analyses = [analysis for analysis, _ in analyses]

            return (
                analyses,
                final_analysis,
                final_verbs,
                final_main_verb,
                final_modal_verbs,
            )

    def _doc_i(self, verb: Tuple[Token, Dict[str, str]]) -> int:
        """Return the index of a verb in a document.
            Use this function for local word order comparisons,
            if the words (but not their indices) are potentially reversed.

        Args:
            verb: A (verb, analysis) tuple.

        Returns:
            The index in the verb complex.
                - `verb.i` for OV languages
                - `len(verb.doc)-verb.i` for VO languages

        """
        verb, _ = verb
        if self.ov:
            return verb.i
        return len(verb.doc) - verb.i

    def _filter_analyses(
        self, analyses: List[Tuple[Dict[str, str], List[Token]]]
    ) -> List[Tuple[Dict[str, str], List[Token]]]:
        """Filter out improbable analyses.

        Args:
            List of (analysis, verbs) tuples.

        Returns:
            Reduced list of (analysis, verbs) tuples.

        """
        # Filter by voice.
        filtered_analyses = []
        for analysis, verbs in analyses:
            verbs_voices = set()
            for verb, verb_analysis in verbs:
                if "Voice" in verb_analysis:
                    verbs_voices.add(verb_analysis["Voice"])
                if verb.dep_.endswith("pass"):
                    verbs_voices.add("Pass")
            analysis_voices = set(analysis["Voice"].split(",") if "Voice" in analysis else [])
            if (
                len(verbs_voices) == 0
                or len(analysis_voices) == 0
                or len(analysis_voices.intersection(verbs_voices)) > 0
            ):
                filtered_analyses.append((analysis, verbs))
        if len(filtered_analyses) > 0:
            analyses = filtered_analyses

        return analyses

    def _get_compound_verb(self, clause: Span) -> List[Token]:
        """Determine the compound verb in a clause.

        Args:
            clause: The clause.

        Returns:
            The words that belong to the compound verb.

        """
        compound_verb = []
        for token in clause._.tokens:
            if token.pos_ in ["AUX", "VERB"]:
                compound_verb.append(token)
            elif self.handle_particles:
                if token.pos_ == "PART" and token.head.pos_ in ["AUX", "VERB"]:
                    compound_verb.append(token)
        return compound_verb

    def _is_match(
        self,
        verb_analyses1: List[Dict[str, str]],
        verb_analyses2: List[Dict[str, str]],
    ) -> Tuple[bool, int]:
        """Check whether two compound verbs are identical.

        Args:
            verb_analyses1: The analyses of the verbs in the first compound verb.
            verb_analyses2: The analyses of the verbs in the second compound verb.

        Returns:
            Whether the two lists of analyses match.
            The number of features that match.

        """
        matched_feats = 0
        for verb_analysis1, verb_analysis2 in zip(verb_analyses1, verb_analyses2):
            lemmas1 = set(verb_analysis1.get("lemma", "#main#").split("|"))
            lemmas2 = set(verb_analysis2.get("lemma", "#main#").split("|"))
            if len(lemmas1.intersection(lemmas2)) == 0:
                return False, -1
            feats1 = set(verb_analysis1.keys())
            feats2 = set(verb_analysis2.keys())
            feats = feats1.intersection(feats2)
            feats.discard("lemma")
            for feat in feats:
                if verb_analysis1[feat] != verb_analysis2[feat]:
                    return False, -1
            matched_feats += len(feats)
        return True, matched_feats

    def _lookup(
        self,
        verbs: List[Tuple[Token, Dict[str, str]]],
        inflection_table: List[Tuple[List[Dict[str, str]], Dict[str, str]]],
    ) -> Set[str]:
        """Map morphological analyses to grammatical analyses.

        Args:
            verbs: The verbs of the compound verb as a list of (verb, analysis) tuples.
            inflection_table: The complete inflection table that defines mappings
                from a list of verb-analyses to a compound verb analysis.

        Returns:
            A set of hashed compound verb analyses.
                The analyses are hashed using `json.dumps`.

        """
        lookup_verbs = []
        for verb, verb_analysis in verbs:
            lookup_verb = {}
            lookup_verb.update(verb_analysis)
            del lookup_verb["Category"]
            if verb_analysis["Category"] == "Aux":
                lookup_verb["lemma"] = verb.lemma_
            lookup_verbs.append(lookup_verb)

        analyses = {}
        for table_verbs, compound_analysis in inflection_table:
            for perm_verbs in (
                itertools.permutations(lookup_verbs)
                if self.handle_local_verb_movement
                else [lookup_verbs]
            ):
                if len(table_verbs) != len(perm_verbs):
                    break
                is_match, matched_feats = self._is_match(table_verbs, perm_verbs)
                if is_match:
                    try:
                        analyses[matched_feats].add(json.dumps((compound_analysis)))
                    except KeyError:
                        analyses[matched_feats] = set([json.dumps((compound_analysis))])

        if len(analyses) == 0:
            return set()
        return analyses[max(analyses.keys())]

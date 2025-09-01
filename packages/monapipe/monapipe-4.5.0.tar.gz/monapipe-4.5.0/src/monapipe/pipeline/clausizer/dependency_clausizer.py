# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any, List

from spacy.language import Language
from spacy.tokens import Doc, Span, Token

from monapipe.lookups import lookup
from monapipe.pipeline.clausizer.clausizer import Clausizer
from monapipe.pipeline.methods import add_extension, requires


@Language.factory(
    "dependency_clausizer",
    assigns=Clausizer.assigns,
    default_config={
        "dep_labels": [
            "acl",
            "advcl",
            "ccomp",
            "conj",
            "csubj",
            "discourse",
            "list",
            "parataxis",
            "root",
            "vocative",
            "xcomp",
        ],
        "conj_rule_labels": ["conj"],
        "xcomp_rule_labels": ["xcomp"],
        "handle_semi_modals": True,
        "include_ws": False,
    },
)
def dependency_clausizer(
    nlp: Language,
    name: str,
    dep_labels: List[str],
    conj_rule_labels: List[str],
    xcomp_rule_labels: List[str],
    handle_semi_modals: bool,
    include_ws: bool,
) -> Any:
    """Spacy component implementation.
        Splits sentences of a document into clauses, buy cutting specific dependency relations.

    Args:
        nlp: Spacy object.
        name: Component name.
        dep_labels: Dependency relations that qualify as root nodes of clauses.
        conj_rule_labels: Dependency relations that qualify as root nodes of conjunctional clauses.
        xcomp_rule_labels: Dependency relations that qualify as root nodes of infinitive clauses.
        handle_semi_modals: False iff semi-modal verbs should always be treated as full verbs.
            Otherwise, they are treated as full verbs or modal verbs depending on context.
        include_ws: True iff whitespace tokens should be included (in this case they are treated as punctuation).
            If so, all tokens of the document are included in a clause. Otherwise, whitespace tokens don't belong to any clause.

    Returns:
        `DependencyClausizer`.

    """
    return DependencyClausizer(
        nlp, dep_labels, conj_rule_labels, xcomp_rule_labels, handle_semi_modals, include_ws
    )


class DependencyClausizer(Clausizer):
    """The class `DependencyClausizer`."""

    def __init__(
        self,
        nlp: Language,
        dep_labels: List[str],
        conj_rule_labels: List[str],
        xcomp_rule_labels: List[str],
        handle_semi_modals: bool,
        include_ws: bool,
    ):
        requires(self, nlp, ["tok2vec", "morphologizer", "lemmatizer", "parser"])

        super().__init__(
            nlp, dep_labels, conj_rule_labels, xcomp_rule_labels, handle_semi_modals, include_ws
        )

        self.dep_labels = set(dep_labels)
        self.conj_rule_labels = set(conj_rule_labels)
        self.xcomp_rule_labels = set(xcomp_rule_labels)
        self.dep_labels.difference_update(self.conj_rule_labels)
        self.dep_labels.difference_update(self.xcomp_rule_labels)

    def __call__(self, doc: Doc) -> Doc:
        semi_modals = lookup(doc.lang_, "semi_modal_verbs")
        all_clauses = []
        for sent in doc.sents:
            clauses = self._find_clauses(list(sent), semi_modals)
            clauses = self._strip_punct_and_convert(doc, clauses)
            clauses = [
                clause for clause in clauses if len(clause) > 0
            ]  # empty spans cause errors when accessing
            clauses = sorted(clauses, key=lambda clause: (clause.start, clause.end))
            sent._.clauses = clauses
            all_clauses.extend(clauses)
        doc._.clauses = all_clauses
        for clause in all_clauses:
            for token in clause._.tokens:
                token._.clause = clause
        return doc

    def _conj_is_clause(self, token: Token) -> bool:
        """Check whether a token is the root of a conjunctional clause.

        Args:
            token: The token.

        Returns:
            boolean: True iff the token's head is the root of a clause.

        """
        dep = token.head.dep_.split(":")[0].lower()
        return dep in self.dep_labels and dep not in self.conj_rule_labels

    def _find_clauses(self, sent: List[Token], semi_modals: List[str]) -> List[List[Token]]:
        """Find all clauses in a sentence.

        Args:
            sent: A list of spacy tokens (e.g. a sentence).
            semi_modals: List of semi-modal verbs.

        Returns:
            List of clauses.

        """
        clauses = {}
        for token in sent:
            clause_head = token
            while not (
                self._is_clause_root(clause_head, semi_modals) or clause_head.head == clause_head
            ):
                clause_head = clause_head.head
            try:
                clauses[clause_head.i].append(token)
            except KeyError:
                clauses[clause_head.i] = [token]
        return list(clauses.values())

    def _is_clause_root(self, token: Token, semi_modals: List[str]) -> bool:
        """Check whether a token is the root of a clause.
            Handles conjunctional and infinitive clauses.

        Args:
            token: The token.
            semi_modals: List of semi-modal verbs.

        Returns:
            boolean: True iff the token is the root of a clause.

        """
        dep = token.dep_.split(":")[0].lower()
        if dep in self.dep_labels:
            return True
        if dep in self.conj_rule_labels:
            return self._conj_is_clause(token)
        if dep in self.xcomp_rule_labels:
            return self._xcomp_is_clause(token, semi_modals)
        return False

    def _strip_punct_and_convert(self, doc: Doc, clauses: List[List[Token]]) -> List[Span]:
        """Convert clauses to spacy spans.
            Preceding and Succeeding punctuation is not included in a span but saved in according attributes of the span.

        Args:
            The parent document.
            List of clauses. Clauses are lists of tokens.

        Returns:
            List of clauses.

        """
        for i, clause in enumerate(clauses):
            succ_punct = []
            for j in range(len(clause)):
                token = clause[-j - 1]
                if token.is_punct or token.is_space:
                    succ_punct.append(token)
                else:
                    break
            prec_punct = []
            if len(succ_punct) < len(clause):
                for j, token in enumerate(clause):
                    if token.is_punct or token.is_space:
                        prec_punct.append(token)
                    else:
                        break
                start = clause[len(prec_punct)].i
                end = clause[-len(succ_punct) - 1].i
                clauses[i] = doc[start : end + 1]
                clauses[i]._.tokens = [token for token in clauses[i] if token in clause]
            else:
                clauses[i] = Doc(doc.vocab, [])[0:0]
                clauses[i]._.tokens = []
            if not self.include_ws:
                prec_punct = [token for token in prec_punct if not token.is_space]
                succ_punct = [token for token in succ_punct if not token.is_space]
            clauses[i]._.prec_punct = prec_punct
            clauses[i]._.succ_punct = list(reversed(succ_punct))
        return clauses

    def _xcomp_is_clause(self, token: Token, semi_modals: List[str]) -> bool:
        """Check whether a token is the root of an infinitive clause.

        Args:
            token: The token.
            semi_modals: List of semi-modal verbs.

        Returns:
            boolean: True iff the token's subtree contains at least a verb form and another word.

        """
        if self.handle_semi_modals and token.head.lemma_ in semi_modals:
            return False
        tokens = token.subtree
        verbs = 0
        words = 0
        for token in tokens:
            if token.is_punct or token.is_space:
                continue
            if token.pos_ in ["VERB", "AUX"]:
                verbs += 1
            else:
                dep = token.dep_.split(":")[0]
                if dep == "compound" or (dep == "mark" and token.pos_ == "PART"):
                    continue
                words += 1
        return verbs > 0 and words > 0

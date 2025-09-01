from typing import List, Set

from spacy.tokens import Doc


def create_passages_from_clause_tags(doc: Doc, attr: str, clause_tags: List[Set[str]]):
    """Creates and adds passage `Span`s to the document.
        If two or more tags are assigned to the same sequence of clauses, they are merged into one passage span.

    Args:
        doc: The document.
        clause_tags: A set of tags for each clause in the document.

    """
    if len(clause_tags) != len(doc._.clauses):
        raise ValueError("Length of `clause_tags` does not match length of `doc._.clauses`.")

    doc.spans[attr] = []

    current_passages = {}  # incomplete passages by tag

    # iterate over the tags for every clause;
    # the last iteration does not correspond to a clause
    # but is necessary to add passages that end with the last clause to `passages`
    for i, tags in enumerate(clause_tags + [set()]):
        passages_to_end = {}  # passages that end before this clause
        for tag in set([t for t in current_passages]).union(tags):
            if tag in current_passages and tag in tags:
                # add the current clause to a current passage
                current_passages[tag].append(i)
            elif tag in current_passages:
                # move a complete passage from `current_passages` to `passages_to_end`
                try:
                    passages_to_end[tuple(current_passages[tag])].add(tag)
                except KeyError:
                    passages_to_end[tuple(current_passages[tag])] = set([tag])
                del current_passages[tag]
            elif tag in tags:
                # create a new current passage
                current_passages[tag] = [i]
        # add the passages to end to `passages`
        for indices, passage_tags in passages_to_end.items():
            passage_clauses = [doc._.clauses[index] for index in indices]
            passage = doc[passage_clauses[0].start : passage_clauses[-1].end]
            setattr(passage._, attr, passage_tags)
            doc.spans[attr].append(passage)

    # sort the passages by start and end
    doc.spans[attr] = sorted(doc.spans[attr], key=lambda passage: (passage.start, passage.end))

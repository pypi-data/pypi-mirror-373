# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any

from spacy.language import Language
from spacy.tokens import Doc

from monapipe.linguistics import get_noun_phrases, is_pronoun, is_proper_noun
from monapipe.lookups import lookup
from monapipe.pipeline.methods import optional, requires
from monapipe.pipeline.speaker_extractor.speaker_extractor import SpeakerExtractor


@Language.factory(
    "rb_speaker_extractor",
    assigns=SpeakerExtractor.assigns,
    default_config={},
)
def rb_speaker_extractor(nlp: Language, name: str) -> Any:
    """Spacy component implementation.
        Extract speaker and addressee for direct speech segments.
        The current implementation is very simple and can only extract explicitly mentioned speakers etc.

    Args:
        nlp: Spacy object.
        name: Component name.

    Returns:
        `RbSpeakerExtractor`.

    """
    return RbSpeakerExtractor(nlp)


class RbSpeakerExtractor(SpeakerExtractor):
    """The class `RbSpeakerExtractor`."""

    def __init__(self, nlp: Language):
        requires(self, nlp, ["lemmatizer", "parser", "speech_tagger"])

        optional(self, nlp, ["ner"])

        super().__init__(nlp)

    def __call__(self, doc: Doc) -> Doc:
        speech_verbs = lookup(doc.lang_, "speech_verbs")
        ents = get_noun_phrases(doc)

        indices = {
            ent.root.i: k for k, ent in enumerate(ents)
        }  # maps a token index to an entity index

        for speech_segment in doc.spans["speech"]:
            if "direct" in speech_segment._.speech:
                start = speech_segment.start
                end = speech_segment.end - 1

                # The next step is to determine the context of the current segment,
                # i.e. the text directly before or after the segment,
                # which potentially contains references to speaker and/or addressee.
                context = []

                # offsets to jump over / "ignore" whitespace tokens between the segment and its context
                offset_a = 1  # offset for context before segment
                while start - offset_a > -1 and doc[start - offset_a].is_space:
                    offset_a += 1
                offset_b = 1  # offset for context after segment
                while end + offset_b < len(doc) and doc[end + offset_b].is_space:
                    offset_b += 1

                # If the token before the segment is a colon or a comma, we choose the preceding tokens as context;
                # otherwise, if the token after the segment is a comma or a verb (but not in a new sentence),
                # we choose the succeeding tokens as context; otherwise, we choose no context.
                # The context always starts before/after the segment and then runs backwards/forwards
                # until a sentence boundary or a new direct speech segment is found.
                if start - offset_a > -2 and doc[start - offset_a].text in [":", ","]:
                    n = start - offset_a
                    while (
                        n > -1 and (not doc[n].is_sent_start) and ("direct" not in doc[n]._.speech)
                    ):
                        context.insert(0, n)
                        n -= 1
                    if n > -1 and "direct" not in doc[n]._.speech:
                        context.insert(0, n)
                elif end + offset_b < len(doc) and (
                    doc[end + offset_b].text == ","
                    or (
                        doc[end + offset_b].pos_ in ["VERB", "AUX"]
                        and not doc[end + offset_b].is_sent_start
                    )
                ):
                    n = end + offset_b
                    while (
                        n < len(doc)
                        and (not doc[n].is_sent_start)
                        and ("direct" not in doc[n]._.speech)
                    ):
                        context.append(n)
                        n += 1

                # Search for potential speakers. These are all subjects within the context:
                subjects = [n for n in context if doc[n].dep_ == "nsubj" and n in indices]

                # Search for potential speech verbs and addressees. Potential addressees are all objects of a verb within the context
                # (currently, we only select NEs and PRONs as potential addressees because NNs are often just adjuncts):
                speech_verbs = []
                other_verbs = []
                for n in context:
                    if doc[n].pos_ == "VERB":
                        objects = [
                            tok.i
                            for tok in doc[n].children
                            if tok.i in context
                            and tok.dep_ in ["obj", "iobj", "obl"]
                            and tok.i in indices
                            and (
                                is_proper_noun(ents[indices[tok.i]])
                                or is_pronoun(ents[indices[tok.i]])
                            )
                        ]
                        if doc[n].lemma_ in speech_verbs:
                            speech_verbs.append((n, objects))
                        else:
                            other_verbs.append((n, objects))

                # Only if no speech verb was found, we consider other verbs:
                verbs = speech_verbs
                if len(speech_verbs) == 0:
                    verbs = other_verbs

                # Choose a speaker from the list of potential speakers.
                # We choose the entitiy which is closest to the speech segment.
                speaker = -1
                if len(subjects) > 0:
                    if subjects[-1] < start:
                        speaker = indices[subjects[-1]]
                    else:
                        speaker = indices[subjects[0]]

                # Choose a verb from the list of potential verbs.
                # We choose the verb which is closest to the speech segment.
                addressee = -1
                if len(verbs) > 0:
                    if verbs[-1][0] < start:
                        _, objects = verbs[-1]
                    else:
                        _, objects = verbs[0]

                    # Choose an addressee from the list of potential addressees.
                    # We choose the addressee which is closest to the speech segment.
                    if len(objects) > 0:
                        if objects[-1] < start:
                            addressee = indices[objects[-1]]
                        else:
                            addressee = indices[objects[0]]

                # Add speaker and addressee to the speech segment.
                if speaker > -1:
                    speech_segment._.speaker = ents[speaker]
                if addressee > -1:
                    speech_segment._.addressee = ents[addressee]

        return doc

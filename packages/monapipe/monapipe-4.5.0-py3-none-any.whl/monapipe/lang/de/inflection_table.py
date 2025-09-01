# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from monapipe.lang.de.auxiliary_verbs import AUXILIARY_VERBS

AUX1 = AUXILIARY_VERBS["AUX1"]  # perfect aspect
AUX2 = AUXILIARY_VERBS["AUX2"]  # passive voice
AUX3 = AUXILIARY_VERBS["AUX3"]  # future tense
AUX4 = AUXILIARY_VERBS["AUX4"]  # copula

INFLECTION_TABLE = [
    (
        [{"VerbForm": "Inf"}, {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"}],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Act",
        },
    ),  # [er] wird sehen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Pass",
        },
    ),  # [er] wird gesehen werden/sein
    (
        [{"VerbForm": "Inf"}, {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"}],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] werde sehen
    (
        [{"VerbForm": "Inf"}, {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"}],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] würde sehen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] werde gesehen werden/sein
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] würde gesehen werden/sein
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Perf",
            "Mood": "Ind",
            "Voice": "Act",
        },
    ),  # [er] wird gesehen haben
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Perf",
            "Mood": "Ind",
            "Voice": "Pass",
        },
    ),  # [er] wird gesehen worden/gewesen sein
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Perf",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] werde gesehen haben
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Perf",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] würde gesehen haben
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Perf",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] werde gesehen worden/gewesen sein
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Inf"},
            {"lemma": AUX3, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Fut",
            "Aspect": "Perf",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] würde gesehen worden/gewesen sein
    (
        [{"VerbForm": "Fin", "Tense": "Past", "Mood": "Ind"}],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Act",
        },
    ),  # [er] sah
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Fin", "Tense": "Past", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Pass",
        },
    ),  # [er] war gesehen worden/gewesen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Fin", "Tense": "Past", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Pass",
        },
    ),  # [er] wurde/war gesehen
    (
        [{"VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"}],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] sähe
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] wäre gesehen worden/gewesen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] würde/wäre gesehen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Fin", "Tense": "Past", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Perf",
            "Mood": "Ind",
            "Voice": "Act",
        },
    ),  # [er] hatte gesehen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Fin", "Tense": "Past", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Past",
            "Aspect": "Perf",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] hätte gesehen
    (
        [{"VerbForm": "Fin", "Tense": "Pres", "Mood": "Imp"}],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Imp",
            "Voice": "Act",
        },
    ),  # sieh!
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Imp"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Imp",
            "Voice": "Pass",
        },
    ),  # werde/sei gesehen!
    (
        [{"VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"}],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Act",
        },
    ),  # [er] sieht
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Pass",
        },
    ),  # [er] ist gesehen worden/gewesen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Ind",
            "Voice": "Pass",
        },
    ),  # [er] wird/ist gesehen
    (
        [{"VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"}],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] sehe
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] sei gesehen worden/gewesen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Imp",
            "Mood": "Sub",
            "Voice": "Pass",
        },
    ),  # [er] werde/sei gesehen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Imp"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Perf",
            "Mood": "Imp",
            "Voice": "Act",
        },
    ),  # habe gesehen!
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Imp"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Perf",
            "Mood": "Imp",
            "Voice": "Pass",
        },
    ),  # sei gesehen worden/gewesen!
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Perf",
            "Mood": "Ind",
            "Voice": "Act",
        },
    ),  # [er] hat gesehen
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX1, "VerbForm": "Fin", "Tense": "Pres", "Mood": "Sub"},
        ],
        {
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Aspect": "Perf",
            "Mood": "Sub",
            "Voice": "Act",
        },
    ),  # [er] habe gesehen
    (
        [{"VerbForm": "Inf"}],
        {"VerbForm": "Inf", "Aspect": "Imp", "Voice": "Act"},
    ),  # (zu) sehen
    (
        [{"VerbForm": "Part", "Aspect": "Perf"}, {"lemma": AUX2, "VerbForm": "Inf"}],
        {"VerbForm": "Inf", "Aspect": "Imp", "Voice": "Pass"},
    ),  # gesehen (zu) werden/sein
    (
        [
            {"VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX2, "VerbForm": "Part", "Aspect": "Perf"},
            {"lemma": AUX4, "VerbForm": "Inf"},
        ],
        {"VerbForm": "Inf", "Aspect": "Imp", "Voice": "Pass"},
    ),  # gesehen worden/gewesen (zu) sein
    (
        [{"VerbForm": "Part", "Aspect": "Perf"}, {"lemma": AUX1, "VerbForm": "Inf"}],
        {"VerbForm": "Inf", "Aspect": "Perf", "Voice": "Act"},
    ),  # gesehen (zu) haben
    (
        [{"VerbForm": "Part", "Aspect": "Imp"}],
        {"VerbForm": "Part", "Tense": "Pres", "Aspect": "Imp"},
    ),  # sehend
    (
        [{"VerbForm": "Part", "Aspect": "Perf"}],
        {"VerbForm": "Part", "Tense": "Past", "Aspect": "Perf"},
    ),  # gesehen
]

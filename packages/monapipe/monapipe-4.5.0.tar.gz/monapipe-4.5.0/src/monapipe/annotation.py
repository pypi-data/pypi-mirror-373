# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

from typing import Any, Iterable, List, Optional, Set


class Annotation:
    """A class that stores information from an annotation."""

    def __init__(
        self, tag, tagset, property_values_dict, tokens, id_value, strings, string_positions
    ):
        self.tag = tag
        self.tagset = tagset
        self.property_values = property_values_dict
        self.tokens = tokens
        self.id = id_value
        self.strings = strings
        self.string_positions = string_positions

    def __repr__(self):
        return str(vars(self))

    def __str__(self):
        return str(vars(self))


class AnnotationList(list):
    """A class that stores a list of Annotation-objectes."""

    def __init__(self, annotation_list: Optional[List[Annotation]] = None):
        if annotation_list is None:
            annotation_list = []
        super().__init__(annotation_list)

    def get_annotations(
        self, tags: Optional[Iterable[str]] = None, tagset: Optional[str] = None
    ) -> Any:
        """Find Annotation-objects with specified tags and tagset.

        Args:
            tags: Tags to search for.
            tagset: Parameter to filter for specific tagset.

        Returns:
            `AnnotationList`: all annotation-objects with specified tags and tagset.
                If `tags` is empty, all tags of the given tagset are searched.
                If `tagset` is None, no filtering for a specific tagset is applied.

        """
        annotations_to_return = AnnotationList()
        for annotation in self:
            if (tags is None or annotation.tag in tags) and (
                tagset is None or annotation.tagset.startswith(tagset)
            ):
                annotations_to_return.append(annotation)
        return annotations_to_return

    def get_tags(
        self, tags: Optional[Iterable[str]] = None, tagset: Optional[str] = None
    ) -> Set[str]:
        """Find all or specified tags in a AnnotationList.

        Args:
            tags: Parameter to filter for specific tags.
            tagset: Parameter to filter for specific tagset.

        Returns:
            All or specified tags that occour in the AnnotationList.

        """
        tags_to_return = set()
        for annotation in self:
            if (tags is None or annotation.tag in tags) and (
                tagset is None or annotation.tagset.startswith(tagset)
            ):
                tags_to_return.add(annotation.tag)
        return tags_to_return

# SPDX-FileCopyrightText: 2022 Georg-August-Universität Göttingen
#
# SPDX-License-Identifier: CC0-1.0

import codecs
import os
import re
import xml.etree.cElementTree as ET
from typing import Any, Dict, List, Optional

from spacy.language import Language
from spacy.tokens import Doc

from monapipe.annotation import Annotation, AnnotationList
from monapipe.pipeline.annotation_reader.annotation_reader import AnnotationReader
from monapipe.pipeline.methods import get_doc_text


@Language.factory(
    "catma_annotation_reader",
    assigns=AnnotationReader.assigns,
    default_config={"corpus_path": None},
)
def catma_annotation_reader(nlp: Language, name: str, corpus_path: Optional[str]) -> Any:
    """Spacy component implementation.
        Reads path to a CATMA collection (a CATMA collection is the
            unzipped tar.gz folder, which contains the annotated text as
            txt and a folder "annotationcollections" with the annotations
            of each annotator as TEI).
        Adds annotation to spacy document object (`Doc`) and spacy token object (`Token`)
            as _.annotations (name to call on spacy object).

        Doc._.annotations returns list of all annotions. Each annotation (list element) contains a dic with:
            - "tagset": tagset name (str)
            - "tag": tag name (str)
            - "property_values": dict with key for each property value (dict)
            - "id": unique id for annotated span (int)
            - "strings": list of str
            - "string_positions": list of tuple with start/end string position for anno in original text
            - "span": List of (Spacy-)Token

    Args:
        nlp: Spacy object.
        name: Component name.
        corpus_path: Path to CATMA collection with a txt-file and TEI-files.
            The TEI files can be stored in an "annotationcollections"-folder or directly in `corpus_path`.

    Returns:
        `CatmaAnnotationReader`.

    """
    return CatmaAnnotationReader(nlp, corpus_path)


class CatmaAnnotationReader(AnnotationReader):
    """The class `CatmaAnnotationReader`."""

    def __init__(self, nlp: Language, corpus_path: Optional[str]):
        super().__init__(nlp, corpus_path)

        # name space for CATMA TEI/XML
        self._namespace = {
            "tei": "http://www.tei-c.org/ns/1.0",
            "xml": "http://www.w3.org/XML/1998/namespace",
        }

    def __call__(self, doc: Doc) -> Doc:
        if self.corpus_path is None:
            return doc

        collection_path = self._find_collection_path(doc)
        if collection_path is None:
            return doc

        annotation_collection = self._read_annotation_(collection_path)

        # 1. assign tokens to character positions for faster look-up
        # 2. assign empty AnnotationLists to every token for every annotator
        charpos_to_token_i = {}
        for token_i, token in enumerate(doc):
            try:
                charpos = token._.idx
            except AttributeError:
                charpos = token.idx
            charpos_to_token_i[charpos] = token_i

            token._.annotations = {}
            for annotator in annotation_collection:
                token._.annotations[annotator] = AnnotationList()

        doc._.annotations = {}
        for annotator, annotations in annotation_collection.items():
            # define each value for doc._.annotations[annotator] as AnnotationList
            doc._.annotations[annotator] = AnnotationList()

            for annotation in annotations:
                token_indices = []
                for string_position_tuple in annotation["string_positions"]:
                    anno_range = range(string_position_tuple[0], string_position_tuple[1])
                    for charpos in anno_range:
                        try:
                            token_indices.append(charpos_to_token_i[charpos])
                        except KeyError:
                            pass

                if len(token_indices) > 0:
                    # define span as list of tokens
                    anno_span = [doc[token_index] for token_index in token_indices]
                    # add Annotation-object to anno_span._.annotation
                    annotation_object = Annotation(
                        tag=annotation["tag"],
                        tagset=annotation["tagset_name"],
                        property_values_dict=annotation["property_values"],
                        tokens=anno_span,
                        id_value=annotation["id"],
                        strings=annotation["strings"],
                        string_positions=annotation["string_positions"],
                    )

                    # append Annotation to AnnotationList for annotator
                    doc._.annotations[annotator].append(annotation_object)

                    # append Annotation to corresponding tokens
                    for token_of_span in anno_span:
                        token_of_span._.annotations[annotator].append(annotation_object)

            doc._.annotations[annotator] = AnnotationList(
                sorted(doc._.annotations[annotator], key=lambda anno: anno.string_positions[0][0])
            )

        return doc

    def _find_collection_path(self, doc: Doc) -> str:
        """Find the annotation collections for a document.

        Args:
            doc: The document.

        Returns:
            The path to the directory with the annotations.
                Returns `None` if no directory is found.

        """
        text = get_doc_text(doc, normalized=False)
        for folder in os.listdir(self.corpus_path):
            folder = os.path.join(self.corpus_path, folder)
            if os.path.isdir(folder):
                for file in os.listdir(folder):
                    file = os.path.join(folder, file)
                    if file.endswith(".txt"):
                        if open(file).read() == text:
                            # piped text was read with `open(...)`
                            return folder
                        elif self._read_annotated_file(file) == text:
                            # piped text was read with `codecs.open(..., encoding="utf8")`
                            return folder
        return None

    def _read_annotated_file(self, text_file: str) -> str:
        """Reads text file with forced utf8 encoding to avoid offset issus.

        Args:
            text_file: A text file.

        Returns:
            The text.

        """
        with codecs.open(text_file, "r", encoding="utf8") as file:
            text = file.read()
            return text

    def _read_annotation(self, tei_file: str, text: str) -> List[Dict[str, Any]]:
        """Stores all annotations of one annotator in list.

        Args:
            tei_file: Annotation in CATMA-TEI-format.
            text: Annotated text.

        Returns:
            List of annotation dictionaries.
            Each list element contains a dic with:
            - "tagset": tagset name (str)
            - "tag": tag name (str)
            - "property_values": dict with key for each property value
            - "id": unique id for annotated span
            - "strings": list of str
            - "string_positions": list of tuple with start/end string position for anno in original text

        """
        with open(tei_file) as f:
            tree = ET.ElementTree(file=f)
            root = tree.getroot()

            annotation_list = []

            # Every fs-Element contains an annotation.
            # Each fs-Element contains information about:
            # - the string position: fs[@xml:id = CATMA-ID] -> points to -> seg-Element[@ana = same CATMA-ID]
            # - the tagset: fs[@xml:type = CATMA-ID] -> points to -> fsDecl[@xml:id = same CATMA-ID]
            # - Property-Values for each anno-span as fs[@attribute_for_prop_value]

            # select fs-element in tei:text (other fs-element in sourceDesc should not be considered)
            fs_list = root.findall("tei:text/tei:fs", self._namespace)
            for index_fs_list, fs in enumerate(fs_list):
                fs_dic = {}

                #################################
                # Find String Positions via @xml:id
                xml_id = fs.attrib["{http://www.w3.org/XML/1998/namespace}id"]

                # if seg[@ana] contains multiple catma-ids: <seg ana="#CATMA_D7AF9100-5264-49BC-BB25-16DE3F5F842B #CATMA_6057DA8D-9438-4DAC-A0C9-9A5F12EC83A4">
                # -> find all segs and check if xml_id is in attrib:
                seg_list = [
                    elm
                    for elm in root.findall(".//tei:seg[@ana]", self._namespace)
                    if xml_id in elm.attrib["ana"]
                ]

                # build list with all character positions as tuples with start/end-char
                chars = []
                for seg in seg_list:
                    ptr_target = seg.find("tei:ptr", self._namespace).attrib["target"]
                    char = re.findall(r"\d+,\d+", ptr_target)
                    char = char[0].split(",")
                    char = (int(char[0]), int(char[1]))
                    chars.append(char)

                string_positions = chars
                fs_dic["string_positions"] = string_positions

                # Find string via string_position
                string_list = []
                for string_position in string_positions:
                    string_list.append(text[string_position[0] : string_position[1]])
                fs_dic["strings"] = string_list

                #################################
                # Find tagset name, tag via @type
                type_ = fs.attrib["type"]
                # tag
                fs_decl = root.findall(".//tei:fsDecl[@xml:id='%s']" % type_, self._namespace)
                # tagset name
                tag = fs_decl[0].find("tei:fsDescr", self._namespace).text
                tagset_name = root.findall(
                    ".//tei:fsDecl[@xml:id='%s']/.." % type_, self._namespace
                )[0].attrib["n"]
                fs_dic["tag"] = tag
                fs_dic["tagset_name"] = tagset_name

                #################################
                # Read Property Values in list:
                property_values = {}
                for f in fs:
                    # select property values (all f.attrib except the in the list below)
                    if f.attrib["name"] not in [
                        "catma_markupauthor",
                        "catma_markuptimestamp",
                        "catma_displaycolor",
                    ]:
                        # if one property value is selected, choose subelement string
                        if len(f.findall("tei:string", self._namespace)) != 0:
                            property_values[f.attrib["name"]] = [
                                f.findall("tei:string", self._namespace)[0].text
                            ]
                        # if more property values are selected, choose subelements ("string") of vRange-Element
                        if len(f.findall("tei:vRange", self._namespace)) != 0:
                            property_values[f.attrib["name"]] = [
                                i.text for i in f.findall(".//tei:string", self._namespace)
                            ]
                fs_dic["property_values"] = property_values

                #################################
                # Add index as identifier for each anno
                fs_dic["id"] = index_fs_list

                #################################
                # Append fs_dic for anno to list with all annos
                annotation_list.append(fs_dic)

            return annotation_list

    def _read_annotation_(self, collection_folder: str) -> Dict[str, List[Dict[str, Any]]]:
        """Automatically choose between `read_annotation_collection` and `read_annotation_files`.

        Args:
            collection_folder: folder with annotation files.

        Returns:
            Dict (annotator as key) of `annotation_lists` from `read_annotation()`.

        """
        if "annotationcollections" in os.listdir(collection_folder):
            return self._read_annotation_collection(collection_folder)
        return self._read_annotation_files(collection_folder)

    def _read_annotation_collection(
        self, collection_folder: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Reads collection of CATMA annotations from the folder "annotationcollections".

        Args:
            collection_folder: collection_folder is the unzipped content of the CATMA-Corpus_Export-XXX.tar.gz
                which is named after the annotated text and which contains a folder "annotationcollections".

        Returns:
            Dict (annotator as key) of `annotation_lists` from `read_annotation()`.

        """
        # collection_folder is the unzipped content of the CATMA-Corpus_Export-XXX.tar.gz
        # which is named after the annotated text, eg. "Doeblin_Die_Ermordung_der_Butterblume",
        # and which contains:
        # - the file itself (eg. "Doeblin_Die_Ermordung_der_Butterblume.txt")
        # - a folder "annotationcollections" with each annotation of that text
        for file in os.listdir(collection_folder):
            if file.endswith(".txt"):
                text_file = file
                text = self._read_annotated_file(os.path.join(collection_folder, text_file))

        annotation_collection = {}
        for folder in os.listdir(collection_folder):
            if folder == "annotationcollections":
                annotationcollections_folder = folder
                for annotation_file in os.listdir(
                    os.path.join(collection_folder, annotationcollections_folder)
                ):
                    if not annotation_file.endswith(".xml"):
                        continue
                    annotation_list = self._read_annotation(
                        os.path.join(
                            collection_folder, annotationcollections_folder, annotation_file
                        ),
                        text,
                    )
                    annotation_collection[annotation_file.strip(".xml")] = annotation_list

        return annotation_collection

    def _read_annotation_files(self, collection_folder: str) -> Dict[str, List[Dict[str, Any]]]:
        """Reads annotation files in CATMA-TEI-format and stores each annotation as `annotation_list`
            in dict with keys for annotators. Files are expected to be in a folder named after the
            corresponding text, eg. "Fontane__Der_Stechlin", which contains annotation files with a
            abrevation of the annotator and a timestamp, eg. "FA_2020-11-12". The newest annotation
            is considered for the annotation collection.

        Args:
            collection_folder: folder with annotation files.

        Returns:
            Dict (annotator as key) of `annotation_lists` from `read_annotation()`.

        """
        for file in os.listdir(collection_folder):
            if file.endswith(".txt"):
                text_file = file
                text = self._read_annotated_file(os.path.join(collection_folder, text_file))

        annotation_collection = {}
        for annotation_file in os.listdir(collection_folder):
            annotator = annotation_file.strip(".xml")
            if not annotation_file.endswith(".xml"):
                continue
            annotation_list = self._read_annotation(
                os.path.join(collection_folder, annotation_file), text
            )
            annotation_collection[annotator] = annotation_list

        return annotation_collection

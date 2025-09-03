import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from docx import Document
from docx.shared import RGBColor

from openpecha.config import PECHAS_PATH
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import AlignmentAnnotation, SapcheAnnotation, span
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.metadata import InitialCreationType
from openpecha.pecha.parsers import BaseParser
from openpecha.utils import parse_alignment_index


class DocxComplexCommentaryParser(BaseParser):
    def __init__(self, root_path: Optional[str] = None):
        self.root_path = root_path
        self.commentary_segment_splitter = "\n\n"
        self.meaning_segment_anns: List[AlignmentAnnotation] = []
        self.sapche_anns: List[SapcheAnnotation] = []
        self.temp_state = {
            "meaning_segment": {"anns": [], "char_diff": 0},
            "sapche": {"anns": [], "char_diff": 0},
        }
        self.base = ""
        self.metadata: Dict[str, Any] = {}

    def normalize_text(self, text: str):
        text = self.normalize_whitespaces(text)
        text = self.normalize_newlines(text)
        return text

    @staticmethod
    def normalize_whitespaces(text: str):
        """
        If there are spaces or tab between newlines, it will be removed.
        """
        return re.sub(r"\n[\s\t]+\n", "\n\n", text)

    @staticmethod
    def normalize_newlines(text: str):
        """
        If there are more than 2 newlines continuously, it will replace it with 2 newlines.
        """
        return re.sub(r"\n{3,}", "\n\n", text)

    def parse(
        self,
        input: Path,
        metadata: Dict,
        output_path: Path = PECHAS_PATH,
    ) -> Pecha:

        # Clean up class attributes
        self.meaning_segment_anns = []
        self.base = ""

        metadata["root_path"] = self.root_path
        self.metadata = metadata
        self.parse_commentary(input)

        pecha = self.create_pecha(output_path)
        return pecha

    def prepare_doc(self, input: Path):
        """
        Input: a docx file
        Process: Prepare the doc for parsing
        """

        def format_paragraphs(paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
            """
            Paragraphs is a text with styles.
            Each line in docx file is a paragraph.
            We have to combine the text and the styles
            """
            formatted_paras = []
            para_texts = []
            for para in paragraphs:
                para_texts.append(para["text"].strip())
                style_texts = []
                styles = []
                for para_style in para["styles"]:
                    para_text = para_style.text
                    style_texts.append(para_text)
                    styles.append(para_style.font)
                if style_texts:
                    style_texts[0] = style_texts[0].lstrip()
                    style_texts[-1] = style_texts[-1].rstrip()
                formatted_paras.append({"texts": style_texts, "styles": styles})
            res = {"text": "\n".join(para_texts), "styles": formatted_paras}
            return res

        # Parse the document
        docs = Document(input)

        formatted_docs = []
        last_doc_data: List[Dict[str, Any]] = []

        for doc in docs.paragraphs:
            if doc.text.strip() == "":
                if last_doc_data:
                    formatted_docs.append(format_paragraphs(last_doc_data))
                    last_doc_data = []
            else:
                last_doc_data.append({"text": doc.text, "styles": doc.runs})

        # Handle remaining paragraphs after the loop
        if last_doc_data:
            formatted_docs.append(format_paragraphs(last_doc_data))

        return formatted_docs

    @staticmethod
    def update_doc(doc: Dict[str, Any], char_diff: int):
        """
        Updates the document by removing characters up to the given char_diff.
        Args:
            doc (Dict[str, Any]): The document to update, containing text and styles.
            char_diff (int): The number of characters to remove from the beginning of the text.
        Returns:
            Dict[str, Any]: The updated document.
        """
        # Update the main text field
        doc["text"] = doc["text"][char_diff:]

        # Extract the first style's texts and styles
        styles = doc["styles"][0]
        texts = styles["texts"]
        style_meta = styles["styles"]

        char_count = 0
        for idx, text_chunk in enumerate(texts):
            if char_count >= char_diff or char_count + len(text_chunk) == char_diff:
                doc["styles"][0]["styles"] = style_meta[idx + 1 :]
                doc["styles"][0]["texts"] = texts[idx + 1 :]
                break

            if char_count + len(text_chunk) > char_diff:
                doc["styles"][0]["styles"] = style_meta[idx:]
                doc["styles"][0]["texts"] = [
                    text_chunk[char_diff - char_count :]
                ] + texts[idx + 1 :]
                break
            char_count += len(text_chunk)

        return doc

    def add_commentary_meaning_ann(
        self, doc: Dict[str, Any], index: int, char_count: int
    ):
        segment = doc["text"]
        match = re.match(r"^([\d\-,]+) ", segment)
        updated_segment = segment
        if match:
            alignment_index = match.group(1)
            segment = segment.replace(alignment_index, "")
            doc = self.update_doc(doc, len(alignment_index) + 1)
            updated_segment = segment.strip()
            curr_segment_ann = AlignmentAnnotation(
                span=span(start=char_count, end=char_count + len(updated_segment)),
                index=index,
                alignment_index=parse_alignment_index(alignment_index),
            )
        else:
            curr_segment_ann = AlignmentAnnotation(
                span=span(start=char_count, end=char_count + len(segment)),
                index=index,
                alignment_index=[],
            )

        self.temp_state["meaning_segment"]["anns"].append(curr_segment_ann)  # type: ignore
        return doc

    def add_sapche_ann(self, doc: Dict[str, Any], char_count: int):
        """
        Extract and process sapche annotations (in Fuchsia/Pink color) from the provided docx file structure.
        Args:
            doc (Dict[str, Any]): The document structure containing styles and text.
            char_count (int): The initial character count for span calculation.
        Returns:
            str: The updated segment text after processing annotations.
        """
        inner_char_count = 0
        sapche_anns: List[SapcheAnnotation] = []
        for doc_style in doc["styles"]:
            for idx in range(len(doc_style["texts"])):
                if doc_style["styles"][idx].color.rgb == RGBColor(0xFF, 0x00, 0x00):
                    match = re.match(r"([\d\.]+)\s", doc_style["texts"][idx])
                    if match:
                        # Extract sapche number and store the char length to update the previous ann spans
                        sapche_number = match.group(1)
                        doc_style["texts"][idx] = doc_style["texts"][idx].replace(
                            f"{sapche_number} ", ""
                        )
                        self.temp_state["sapche"]["char_diff"] += len(sapche_number)  # type: ignore

                        start = char_count + inner_char_count
                        end = start + len(doc_style["texts"][idx])
                        sapche_anns.append(
                            SapcheAnnotation(
                                span=span(start=start, end=end),
                                sapche_number=sapche_number,
                            )
                        )
                    # If the sapche number is not needed, use the following code in future
                    # else:
                    #     start = char_count + inner_char_count
                    #     end = start + len(doc_style["texts"][idx])
                    #     sapche_anns.append(
                    #         {
                    #             AnnotationType.sapche.value: {
                    #                 "start": start,
                    #                 "end": end,
                    #             }
                    #         }
                    #     )
                inner_char_count += len(doc_style["texts"][idx])
            inner_char_count += 1  # for newline

        formatted_anns = self.merge_anns(sapche_anns, AnnotationType.SAPCHE)
        self.temp_state["sapche"]["anns"].extend(formatted_anns)  # type: ignore
        updated_segment = "\n".join(
            ["".join(doc_style["texts"]) for doc_style in doc["styles"]]
        )
        return updated_segment

    @staticmethod
    def merge_anns(
        anns: List[SapcheAnnotation], ann_layer: AnnotationType
    ) -> List[SapcheAnnotation]:
        """
        Merge overlapping or consecutive sapche annotations.
        Args:
            annotations (List[Dict[str, Any]]): Eg: List of sapche annotations.

        Returns:
            List[Dict[str, Any]]: Merged annotations.
        """
        formatted_anns: List[SapcheAnnotation] = []
        last_ann: Optional[SapcheAnnotation] = None
        for ann in anns:
            if last_ann is None:
                last_ann = ann
                continue
            if ann.span.start != last_ann.span.end:
                formatted_anns.append(last_ann)
                last_ann = ann
            else:
                last_ann[ann_layer.value].span.end = ann.span.end

        if last_ann:
            formatted_anns.append(last_ann)
        return formatted_anns

    def update_ann_spans(self):
        """
        Update the spans of the meaning_segment and sapche annotations.
        """
        if self.temp_state["meaning_segment"]["anns"]:
            meaning_segment_ann = self.temp_state["meaning_segment"]["anns"][0]  # type: ignore
            meaning_segment_ann.span.end -= self.temp_state["sapche"]["char_diff"]
            self.meaning_segment_anns.append(meaning_segment_ann)

        self.sapche_anns.extend(self.temp_state["sapche"]["anns"])  # type: ignore

        self.temp_state = {
            "meaning_segment": {"anns": [], "char_diff": 0},
            "sapche": {"anns": [], "char_diff": 0},
        }

    def parse_commentary(self, input: Path):
        """
        Input: a docx file
        Process: - Parse and record the commentary annotations in self.meaning_segment_anns,
                 - Save the cleaned base text in self.base
        """
        formatted_docs = self.prepare_doc(input)

        char_count = 0
        base_texts = []
        for index, doc in enumerate(formatted_docs):
            segment = doc["text"]
            if not segment:
                continue

            doc = self.add_commentary_meaning_ann(doc, index, char_count)
            updated_segment = self.add_sapche_ann(doc, char_count)

            self.update_ann_spans()

            base_texts.append(updated_segment)
            char_count += len(updated_segment)
            char_count += 2  # for two newlines

        self.base = "\n\n".join(base_texts)

    def create_pecha(self, output_path: Path) -> Pecha:
        pecha = Pecha.create(output_path)
        basename = pecha.set_base(self.base)

        # Add meaning_segment layer
        meaning_segment_layer, _ = pecha.add_layer(basename, AnnotationType.ALIGNMENT)
        for ann in self.meaning_segment_anns:
            pecha.add_annotation(meaning_segment_layer, ann, AnnotationType.ALIGNMENT)
        meaning_segment_layer.save()

        # Add sapche layer
        sapche_layer, _ = pecha.add_layer(basename, AnnotationType.SAPCHE)
        for ann in self.sapche_anns:
            pecha.add_annotation(sapche_layer, ann, AnnotationType.SAPCHE)
        sapche_layer.save()

        pecha.set_metadata(
            {
                "id": pecha.id,
                "parser": self.name,
                "initial_creation_type": InitialCreationType.google_docx,
                **self.metadata,
            }
        )

        return pecha

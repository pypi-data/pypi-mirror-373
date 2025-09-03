import re
from pathlib import Path
from typing import Dict, List, Tuple

from openpecha.config import get_logger
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import BaseAnnotation, FootnoteAnnotation, span
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers import update_coords
from openpecha.pecha.parsers.docx.utils import read_docx

logger = get_logger(__name__)


class DocxFootnoteParser:
    def __init__(self):
        self.footnote_number = r"----footnote(\d+)----"
        self.footnote_content = r"footnote(\d+)\)[\t\s]+(.+)"

    def get_footnote_contents(self, text: str) -> Tuple[str, Dict[int, str]]:
        """
        Extract and remove footnote contents from text.
        """
        matches = re.findall(self.footnote_content, text)
        footnote_contents: Dict[int, str] = {}

        for match in matches:
            footnote_number = int(match[0]) + 1  # footnote number starts from 0
            footnote_content = match[1]
            footnote_contents[footnote_number] = footnote_content

        text = re.sub(self.footnote_content, "", text)
        logger.info(f"Footnote content successfully extracted: {footnote_contents}")
        return (text, footnote_contents)

    def get_footnote_spans(
        self, text: str, footnote_contents: Dict[int, str]
    ) -> Tuple[str, Dict[int, Tuple[int, int]]]:
        matches = re.finditer(self.footnote_number, text)
        footnote_spans: Dict[int, Tuple[int, int]] = {}

        offset = 0

        for match in matches:
            footnote_number = int(match.group(1)) + 1  # footnote number starts from 0
            if footnote_number in footnote_contents:
                start_pos = match.start() - offset
                footnote_spans[footnote_number] = (start_pos, start_pos)

            offset += match.end() - match.start()

        text = re.sub(self.footnote_number, "", text)
        logger.info(f"Footnote spans successfully extracted: {footnote_spans}")
        return (text, footnote_spans)

    def create_footnote_annotations(
        self,
        footnote_spans: Dict[int, Tuple[int, int]],
        footnote_contents: Dict[int, str],
    ) -> List[FootnoteAnnotation]:
        return [
            FootnoteAnnotation(
                index=footnote_number,
                span=span(start=Span[0], end=Span[1]),
                note=footnote_contents[footnote_number],
            )
            for footnote_number, Span in footnote_spans.items()
        ]

    def add_footnote_layer(
        self, pecha: Pecha, anns: List[BaseAnnotation], ann_type: AnnotationType
    ):

        basename = list(pecha.bases.keys())[0]
        layer, layer_path = pecha.add_layer(basename, ann_type)
        for ann in anns:
            pecha.add_annotation(layer, ann, ann_type)
        layer.save()

        return str(layer_path.relative_to(pecha.layer_path))

    def parse(self, pecha: Pecha, input: str | Path) -> str:
        logger.info(f"Parsing footnote annotation for {pecha.id}")
        text = read_docx(docx_file=input, ignore_footnotes=False)
        text, footnote_contents = self.get_footnote_contents(text)
        text, footnote_spans = self.get_footnote_spans(text, footnote_contents)

        anns: List[FootnoteAnnotation] = self.create_footnote_annotations(
            footnote_spans, footnote_contents
        )

        new_base = pecha.get_base(list(pecha.bases.keys())[0])
        anns = update_coords(anns, text, new_base)

        annotation_path: str = self.add_footnote_layer(
            pecha, anns, AnnotationType.FOOTNOTE
        )
        logger.info(f"Footnote annotation successfully added to Pecha {pecha.id}")
        return annotation_path

from pathlib import Path
from typing import Any, List, Tuple

from stam import AnnotationStore

from openpecha.config import get_logger
from openpecha.exceptions import ParseNotReadyForThisAnnotation
from openpecha.pecha import Pecha, annotation_path, get_anns
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers import update_coords
from openpecha.pecha.parsers.docx.commentary.simple import DocxSimpleCommentaryParser
from openpecha.pecha.parsers.docx.footnote import DocxFootnoteParser
from openpecha.pecha.parsers.docx.root import DocxRootParser
from openpecha.pecha.pecha_types import is_root_related_pecha

pecha_id = str

logger = get_logger(__name__)


class DocxAnnotationParser:
    def __init__(self):
        pass

    def add_annotation(
        self,
        pecha: Pecha,
        type: AnnotationType | str,
        docx_file: Path,
        metadatas: List[Any],
    ) -> Tuple[Pecha, annotation_path]:

        # Accept both str and AnnotationType, convert str to AnnotationType
        if isinstance(type, str):
            try:
                type = AnnotationType(type)
            except ValueError:
                raise ParseNotReadyForThisAnnotation(f"Invalid annotation type: {type}")

        if type not in [
            AnnotationType.ALIGNMENT,
            AnnotationType.SEGMENTATION,
            AnnotationType.FOOTNOTE,
        ]:
            raise ParseNotReadyForThisAnnotation(
                f"Parser is not ready for the annotation type: {type}"
            )

        new_basename = list(pecha.bases.keys())[0]
        new_base = pecha.get_base(new_basename)

        if type == AnnotationType.FOOTNOTE:
            footnote_parser = DocxFootnoteParser()
            annotation_path = footnote_parser.parse(pecha, docx_file)
            return (pecha, annotation_path)

        elif is_root_related_pecha(metadatas):
            parser = DocxRootParser()
            anns, old_base = parser.extract_anns(docx_file, AnnotationType.SEGMENTATION)

            updated_anns = update_coords(anns, old_base, new_base)
            logger.info(f"Updated Coordinate: {updated_anns}")

            annotation_path = parser.add_segmentation_layer(pecha, updated_anns, type)
            anns = get_anns(
                AnnotationStore(file=str(pecha.layer_path / annotation_path))
            )
            logger.info(f"New Updated Annotations: {anns}")

            logger.info(
                f"Alignment Annotation is successfully added to Pecha {pecha.id}"
            )
            return (pecha, annotation_path)

        else:
            commentary_parser = DocxSimpleCommentaryParser()
            (
                anns,
                old_base,
            ) = commentary_parser.extract_anns(docx_file, type)

            updated_coords = update_coords(anns, old_base, new_base)
            annotation_path = commentary_parser.add_segmentation_layer(
                pecha, updated_coords, type
            )
            logger.info(
                f"Alignment Annotation is successfully added to Pecha {pecha.id}"
            )
            return (pecha, annotation_path)

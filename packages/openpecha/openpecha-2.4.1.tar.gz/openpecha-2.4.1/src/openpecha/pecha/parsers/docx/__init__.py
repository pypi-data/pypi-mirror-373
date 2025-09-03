from pathlib import Path
from typing import Any, Dict, List, Tuple

from openpecha.config import get_logger
from openpecha.exceptions import ParseNotReadyForThisAnnotation
from openpecha.pecha import Pecha, annotation_path
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers.docx.commentary.simple import DocxSimpleCommentaryParser
from openpecha.pecha.parsers.docx.root import DocxRootParser

logger = get_logger(__name__)


class DocxParser:
    def is_commentary_pecha(self, metadatas: List[Any]) -> bool:
        """Checks if the given metadata corresponds to a commentary Pecha.

        Args:
            metadatas (List[Dict]): List of dictionaries containing metadata of the Pecha.

        Returns:
            bool: True if the Pecha is a commentary, otherwise False.
        """
        for metadata in metadatas:
            if metadata.type == "commentary":
                return True
        return False

    def parse(
        self,
        docx_file: str | Path,
        annotation_type: AnnotationType | str,
        metadatas: List[Any],
        pecha_id: str | None = None,
    ) -> Tuple[Pecha, annotation_path]:
        """Parses a DOCX file and generates a Pecha object based on its type.

        Args:
            docx_file (str | Path): Path to the DOCX file to be parsed.
            metadatas (List[Dict]): List of dictionaries, where each dictionary
                                    contains metadata of the Pecha.
            output_path (Path):
            pecha_id (str | None, optional): Pecha ID to be assigned. Defaults to None.

        Returns:
            Pecha: Pecha object.
        """

        # Accept both str and AnnotationType, convert str to AnnotationType
        if isinstance(annotation_type, str):
            try:
                annotation_type = AnnotationType(annotation_type)
            except ValueError:
                raise ParseNotReadyForThisAnnotation(
                    f"Invalid annotation type: {annotation_type}"
                )

        is_commentary = self.is_commentary_pecha(metadatas)

        # Convert metadata: MetadataModel to Dict
        metadata = metadatas[0].model_dump()

        if is_commentary:
            pecha, annotation_path = DocxSimpleCommentaryParser().parse(
                input=docx_file,
                annotation_type=annotation_type,
                metadata=metadata,
                pecha_id=pecha_id,
            )
            return (pecha, annotation_path)
        else:
            pecha, annotation_path = DocxRootParser().parse(
                input=docx_file,
                annotation_type=annotation_type,
                metadata=metadata,
                pecha_id=pecha_id,
            )
            return (pecha, annotation_path)

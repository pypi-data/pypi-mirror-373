from pathlib import Path
from typing import Any, List
from unittest.mock import patch

from openpecha.pecha import Pecha
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers.docx.annotation import DocxAnnotationParser


class DocxAnnotationUpdate:
    def __init__(self):
        self.parser = DocxAnnotationParser()

    def extract_layer_name(self, layer_path: str) -> str:
        return Path(layer_path).stem

    def extract_layer_id(self, layer_path: str) -> str:
        layer_name = self.extract_layer_name(layer_path)
        return layer_name.split("-")[-1]

    def extract_layer_enum(self, layer_path: str) -> AnnotationType:
        layer_name = self.extract_layer_name(layer_path)
        return AnnotationType(layer_name.split("-")[0])

    def update_annotation(
        self,
        pecha: Pecha,
        annotation_path: str,
        docx_file: Path,
        metadatas: List[Any],
    ) -> Pecha:
        type = self.extract_layer_enum(annotation_path)
        layer_id = self.extract_layer_id(annotation_path)

        with patch("openpecha.pecha.get_layer_id") as mock_layer_id:
            mock_layer_id.return_value = layer_id
            updated_pecha, _ = self.parser.add_annotation(
                pecha, type, docx_file, metadatas
            )

        return updated_pecha

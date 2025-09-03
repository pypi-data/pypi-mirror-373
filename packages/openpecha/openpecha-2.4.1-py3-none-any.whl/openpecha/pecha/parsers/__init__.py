from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Tuple

from openpecha.config import PECHAS_PATH, get_logger
from openpecha.exceptions import MetaDataValidationError
from openpecha.pecha import Pecha, annotation_path
from openpecha.pecha.annotations import BaseAnnotation
from openpecha.pecha.blupdate import DiffMatchPatch
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.metadata import InitialCreationType, PechaMetaData

logger = get_logger(__name__)


class DocxBaseParser(ABC):
    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def parse(
        self,
        input: str | Path,
        annotation_type: AnnotationType,
        metadata: Dict,
        output_path: Path = PECHAS_PATH,
    ) -> Tuple[Pecha, annotation_path]:
        raise NotImplementedError

    def create_pecha(
        self, base: str, output_path: Path, metadata: Dict, pecha_id: str | None
    ) -> Pecha:
        pecha = Pecha.create(output_path, pecha_id)
        pecha.set_base(base)

        try:
            pecha_metadata = PechaMetaData(
                id=pecha.id,
                parser=self.name,
                **metadata,
                bases={},
                initial_creation_type=InitialCreationType.google_docx,
            )
        except Exception as e:
            logger.error(f"The metadata given was not valid. {str(e)}")
            raise MetaDataValidationError(
                f"[Error] The metadata given was not valid. {str(e)}"
            )
        else:
            pecha.set_metadata(pecha_metadata.to_dict())

        return pecha

    def add_segmentation_layer(
        self, pecha: Pecha, anns: List[BaseAnnotation], ann_type: AnnotationType
    ) -> annotation_path:

        basename = list(pecha.bases.keys())[0]
        layer, layer_path = pecha.add_layer(basename, ann_type)
        for ann in anns:
            pecha.add_annotation(layer, ann, ann_type)
        layer.save()

        return str(layer_path.relative_to(pecha.layer_path))


class BaseParser(ABC):
    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def parse(
        self,
        input: Any,
        metadata: Dict,
        output_path: Path = PECHAS_PATH,
    ):
        raise NotImplementedError


class DummyParser(BaseParser):
    @property
    def name(self):
        return self.__class__.__name__

    def parse(
        self,
        input: Any,
        metadata: Dict,
        output_path: Path = PECHAS_PATH,
    ) -> Pecha:
        raise NotImplementedError


class OCRBaseParser(ABC):
    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def parse(
        self,
        dataprovider: Any,
    ) -> Pecha:
        raise NotImplementedError


def update_coords(
    anns: List[BaseAnnotation],
    old_base: str,
    new_base: str,
):
    """
    Update the start/end coordinates of the annotations from old base to new base
    """
    diff_update = DiffMatchPatch(old_base, new_base)
    for ann in anns:
        start = ann.span.start
        end = ann.span.end

        ann.span.start = diff_update.get_updated_coord(start)
        ann.span.end = diff_update.get_updated_coord(end)

    return anns

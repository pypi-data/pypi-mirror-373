from enum import Enum

from openpecha.exceptions import InValidAnnotationLayerName


class AnnotationCollectionType(str, Enum):
    """In STAM, this is used for setting DataSet id"""

    STRUCTURE_ANNOTATION = "structure_annotation"
    VARIATION_ANNOTATION = "variation_annotation"
    OCR_ANNOTATION = "ocr_annotation"
    LANGUAGE_ANNOTATION = "language_annotation"
    SEGMENTATION_ANNOTATION = "segmentation_annotation"


class AnnotationGroupType(str, Enum):
    STRUCTURE_TYPE = "structure_type"
    SPELLING_VARIATION = "spelling_variation"
    OCR_CONFIDENCE_TYPE = "ocr_confidence_type"
    LANGUAGE_TYPE = "language_type"
    SEGMENTATION_TYPE = "segmentation_type"


class AnnotationType(str, Enum):
    SEGMENTATION = "segmentation"
    ALIGNMENT = "alignment"

    VERSION = "version"

    FOOTNOTE = "footnote"

    CHAPTER = "chapter"
    PAGINATION = "pagination"
    DURCHEN = "durchen"
    SAPCHE = "sapche"

    OCR_CONFIDENCE = "ocr_confidence"
    LANGUAGE = "language"
    CITATION = "citation"
    BOOK_TITLE = "book_title"

    @property
    def annotation_collection_type(self):
        return get_annotation_collection_type(self)

    @property
    def annotation_group_type(self):
        return get_annotation_group_type(self)


def get_annotation_type(layer_name: str):
    try:
        return AnnotationType(layer_name)
    except ValueError:
        raise InValidAnnotationLayerName(
            f"Layer name {layer_name} is not associated with any Annotation."
        )


def get_annotation_group_type(layer_type: AnnotationType) -> AnnotationGroupType:
    """return the annotation category where annotation type falls in"""

    if layer_type in [AnnotationType.SEGMENTATION, AnnotationType.ALIGNMENT]:
        return AnnotationGroupType.SEGMENTATION_TYPE

    if layer_type == AnnotationType.VERSION:
        return AnnotationGroupType.SPELLING_VARIATION

    if layer_type in [
        AnnotationType.CHAPTER,
        AnnotationType.SAPCHE,
        AnnotationType.PAGINATION,
        AnnotationType.FOOTNOTE,
    ]:
        return AnnotationGroupType.STRUCTURE_TYPE

    if layer_type == AnnotationType.LANGUAGE:
        return AnnotationGroupType.LANGUAGE_TYPE

    if layer_type == AnnotationType.OCR_CONFIDENCE:
        return AnnotationGroupType.OCR_CONFIDENCE_TYPE

    if layer_type == AnnotationType.DURCHEN:
        return AnnotationGroupType.SPELLING_VARIATION

    raise ValueError(f"Layer type {layer_type} has no defined AnnotationGroupType")


def get_annotation_collection_type(
    layer_type: AnnotationType,
) -> AnnotationCollectionType:
    """return the annotation category where annotation type falls in"""

    if layer_type in [AnnotationType.SEGMENTATION, AnnotationType.ALIGNMENT]:
        return AnnotationCollectionType.SEGMENTATION_ANNOTATION

    if layer_type == AnnotationType.VERSION:
        return AnnotationCollectionType.VARIATION_ANNOTATION

    if layer_type in [
        AnnotationType.CHAPTER,
        AnnotationType.SAPCHE,
        AnnotationType.PAGINATION,
        AnnotationType.FOOTNOTE,
    ]:
        return AnnotationCollectionType.STRUCTURE_ANNOTATION

    if layer_type == AnnotationType.LANGUAGE:
        return AnnotationCollectionType.LANGUAGE_ANNOTATION

    if layer_type == AnnotationType.OCR_CONFIDENCE:
        return AnnotationCollectionType.OCR_ANNOTATION

    if layer_type == AnnotationType.DURCHEN:
        return AnnotationCollectionType.VARIATION_ANNOTATION

    raise ValueError(f"Layer type {layer_type} has no defined AnnotationCollectionType")

from enum import Enum
from typing import Any, Dict, List

from openpecha.config import get_logger
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import AnnotationModel

logger = get_logger(__name__)


class PechaType(Enum):
    """
    Pecha Type for Serializer to determine the type of Pecha.
    """

    root_pecha = "root_pecha"
    root_translation_pecha = "root_translation_pecha"

    commentary_pecha = "commentary_pecha"
    commentary_translation_pecha = "commentary_translation_pecha"

    prealigned_root_translation_pecha = "prealigned_root_translation_pecha"

    prealigned_commentary_pecha = "prealigned_commentary_pecha"
    prealigned_commentary_translation_pecha = "prealigned_commentary_translation_pecha"


def get_aligned_id(ann_models: List[AnnotationModel], annotation_path: str):
    """
    Get the alignment id from List of AnnotationModel
    """
    for ann_model in ann_models:
        if annotation_path == ann_model.path:
            aligned_to = ann_model.aligned_to
            if aligned_to and aligned_to.alignment_id:
                return aligned_to.alignment_id
    return None


def get_pecha_type(
    pechas: List[Pecha],
    metadatas: List[Any],
    annotations: Dict[str, List[AnnotationModel]],
    annotation_path: str,
) -> PechaType:
    is_commentary = is_commentary_pecha(metadatas)
    is_translation = is_translation_pecha(metadatas)

    if is_commentary:
        if is_translation:
            if has_version_of(pechas, annotations, annotation_path):
                return PechaType.prealigned_commentary_translation_pecha
            return PechaType.commentary_translation_pecha
        if has_version_of(pechas, annotations, annotation_path):
            return PechaType.prealigned_commentary_pecha

        return PechaType.commentary_pecha
    else:
        if is_translation:
            if has_version_of(pechas, annotations, annotation_path):
                return PechaType.prealigned_root_translation_pecha
            return PechaType.root_translation_pecha
        return PechaType.root_pecha


def is_commentary_pecha(metadatas: List[Any]) -> bool:
    """
    Pecha can be i) Root Pecha ii) Commentary Pecha
    Output: True if Commentary Pecha, False otherwise
    """
    for metadata in metadatas:
        if metadata.type == "commentary":
            return True
    return False


def is_translation_pecha(metadatas: List[Any]) -> bool:
    """
    Return
        True if i) Translation of Root Pecha ii) Translation of Commentary Pecha
        False otherwise
    """
    if metadatas[0].type == "translation":
        return True
    return False


def has_version_of(
    pechas: List[Pecha],
    annotations: Dict[str, List[AnnotationModel]],
    annotation_path: str,
) -> bool:
    """
    Return
        True: If the pecha points to an alignment annotation layer of Root Pecha
        False: otherwise
    """
    root_pecha = pechas[-1]
    parent_pecha = pechas[-2]

    logger.info(f"Annotations: {annotations}")
    logger.info(f"Root Pecha Annotations: {annotations[root_pecha.id]}")
    logger.info(f"Commentary Pecha Annotations: {annotations[parent_pecha.id]}")

    if len(annotations.keys()) == 3:
        annotation_path = get_aligned_id(annotations[pechas[0].id], annotation_path)

    associated_root_alignment_id = get_aligned_id(
        annotations[parent_pecha.id], annotation_path
    )

    if associated_root_alignment_id.split("/")[1].startswith("alignment"):
        return True
    return False


def is_root_related_pecha(metadatas: List[Any]) -> bool:
    """
    Returns True if the pecha type is root-related.
    """
    for metadata in metadatas:
        if metadata.type == "commentary":
            return False
    return True

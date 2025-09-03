import shutil
import tempfile
from pathlib import Path

from diff_match_patch import diff_match_patch

from openpecha.config import get_logger
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import (
    Pagination,
    SegmentationAnnotation,
    span,
    Version,
    VersionVariantOperations,
)
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers import update_coords
from openpecha.pecha.serializers.json import JsonSerializer

logger = get_logger(__name__)


class EditionParser:
    """
    Parser for extracting segmentation and spelling variant annotations from DOCX files.
    Only used in test context.
    """

    def __init__(self) -> None:
        self.dmp = diff_match_patch()
        self.dmp.Diff_Timeout = 0
        self.dmp.Diff_EditCost = 4
        self.dmp.Match_Threshold = 0.5
        self.dmp.Match_Distance = 100
        self.dmp.Patch_DeleteThreshold = 0.5
        # Patch_Margin and Match_MaxBits can remain defaults

    def parse_segmentation(self, segments: list[str]) -> list[SegmentationAnnotation]:
        """
        Extract text from txt and calculate coordinates for segments.
        """
        anns = []
        char_count = 0
        for index, segment in enumerate(segments, start=1):
            anns.append(
                SegmentationAnnotation(
                    span=span(start=char_count, end=char_count + len(segment)),
                    index=index,
                )
            )
            char_count += len(segment) + 1

        logger.info(f"Parsed {len(anns)} Segmentation Annotations.")
        return anns

    def parse_version(self, source: str, target: str) -> list[Version]:
        """
        Compute version variant annotations (insertions/deletions) between source and target strings.
        """
        diffs = self.dmp.diff_main(source, target, checklines=True)
        self.dmp.diff_cleanupSemantic(diffs)

        anns = []
        char_count = 0
        for marker, text in diffs:
            if marker == 0:
                char_count += len(text)

            elif marker == 1:
                # Insertion
                anns.append(
                    Version(
                        span=span(start=char_count, end=char_count),
                        operation=VersionVariantOperations.INSERTION,
                        text=text,
                    )
                )
            else:
                # Deletion
                anns.append(
                    Version(
                        span=span(start=char_count, end=char_count + len(text)),
                        operation=VersionVariantOperations.DELETION,
                    )
                )
                char_count += len(text)

        logger.info(f"Parsed {len(anns)} Segmentation Annotations.")
        return anns

    def add_pagination_layer(
        self, pecha: Pecha, edition_layer_path: str, pagination_anns: list[Pagination]
    ) -> tuple[Pecha, str]:
        """
        Parse pagination annotations for a given Pecha object and edition layer.

        Args:
            pecha (Pecha): The Pecha object containing the base text and layers.
            edition_layer_name (str): The name of the edition's spelling variant layer to which pagination annotation is build on.
            pagination_anns (list[Pagination]): A list of Pagination annotation objects to process.

        Returns:
            list[Pagination]: A list of processed Pagination annotation objects.
        """
        serializer = JsonSerializer()
        edition_base = serializer.get_edition_base(pecha, edition_layer_path)
        edition_basename = Path(edition_layer_path).stem
        logger.info(f"Retrieved edition base for {edition_basename}")

        output_path = Path(tempfile.mkdtemp())
        temp_pecha = Pecha.create(output_path)
        temp_pecha.set_base(edition_base, edition_basename)

        layer, new_layer_path = temp_pecha.add_layer(
            edition_basename, AnnotationType.PAGINATION
        )
        for ann in pagination_anns:
            pecha.add_annotation(layer, ann, AnnotationType.PAGINATION)

        layer.save()

        # Copy Pagination JSON annotation file to pecha.
        pecha_basename = Path(edition_layer_path).parent
        tgt_path = pecha.layer_path / pecha_basename / new_layer_path.name
        shutil.copy(new_layer_path.as_posix(), tgt_path.as_posix())

        rel_path = str(tgt_path.relative_to(pecha.layer_path))
        logger.info(f"Pagination layer added at {rel_path}")
        return (pecha, rel_path)

    def parse(self, pecha: Pecha, segments: list[str]):
        """
        Parse the DOCX file and add segmentation and version layers to the Pecha.
        Returns the relative paths to the created layers.
        """
        old_basename = list(pecha.bases.keys())[0]
        old_base = pecha.get_base(old_basename)

        new_base = "".join(segments)

        seg_anns = self.parse_segmentation(segments)
        updated_seg_anns = update_coords(seg_anns, old_base, new_base)
        version_anns = self.parse_version(old_base, new_base)

        _, seg_layer_path = self.add_segmentation_layer(pecha, updated_seg_anns)
        _, version_layer_path = self.add_version_layer(pecha, version_anns)

        return seg_layer_path, version_layer_path

    def add_segmentation_layer(
        self, pecha: Pecha, anns: list[SegmentationAnnotation]
    ) -> tuple[Pecha, str]:
        """
        Add a segmentation layer to the Pecha and return its relative path.
        """
        basename = list(pecha.bases.keys())[0]
        layer, layer_path = pecha.add_layer(basename, AnnotationType.SEGMENTATION)
        for ann in anns:
            pecha.add_annotation(layer, ann, AnnotationType.SEGMENTATION)
        layer.save()

        relative_layer_path = str(layer_path.relative_to(pecha.layer_path))
        return (pecha, relative_layer_path)

    def add_version_layer(self, pecha: Pecha, anns: list[Version]) -> tuple[Pecha, str]:
        """
        Add a spelling variant layer to the Pecha and return its relative path.
        """
        basename = list(pecha.bases.keys())[0]
        layer, layer_path = pecha.add_layer(basename, AnnotationType.VERSION)
        for ann in anns:
            pecha.add_annotation(layer, ann, AnnotationType.VERSION)
        layer.save()

        relative_layer_path = str(layer_path.relative_to(pecha.layer_path))
        return (pecha, relative_layer_path)

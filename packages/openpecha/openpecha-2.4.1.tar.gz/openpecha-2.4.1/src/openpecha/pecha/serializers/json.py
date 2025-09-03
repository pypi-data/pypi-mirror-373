import shutil
import tempfile
from pathlib import Path

from stam import AnnotationStore

from openpecha.config import get_logger
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import VersionVariantOperations
from openpecha.pecha.layer import (
    AnnotationType,
    get_annotation_group_type,
    get_annotation_type,
)
from openpecha.pecha.annotations import PechaJson, AlignedPechaJson
from openpecha.alignment import TranslationAlignmentMapping

logger = get_logger(__name__)


class JsonSerializer:
    def get_annotations(self, pecha: Pecha, annotation_paths: list[str]):
        annotations = {}
        for annotation_path in annotation_paths:
            logger.info(f"Processing layer path: {annotation_path}")
            ann_store = AnnotationStore(file=str(pecha.layer_path / annotation_path))
            ann_type = self._get_ann_type(annotation_path)
            annotations[ann_type.value] = self.to_dict(ann_store, ann_type)
        return annotations
    

    def get_annotation(self, pecha: Pecha, annotation_paths: list[str], annotation_id: str):
        annotations = {}
        for annotation_path in annotation_paths:
            ann_store = AnnotationStore(file=str(pecha.layer_path / annotation_path))
            ann_type = self._get_ann_type(annotation_path)
            ann_id = annotation_path.split("/")[1][(len(ann_type.value)+1):-5]
            if ann_id == annotation_id: 
                if ann_type.value not in annotations:
                    annotations[ann_type.value] = {}
                annotations[ann_type.value][ann_id] = self.to_dict(ann_store, ann_type)
                return annotations
        raise ValueError(f"Annotation with id {annotation_id} not found")


    def get_base(self, pecha: Pecha):
        basename = list(pecha.bases.keys())[0]
        base = pecha.get_base(basename)
        logger.info(
            f"Retrieved base text from Pecha '{pecha.id}' (basename: {basename})."
        )
        return base

    @staticmethod
    def to_dict(ann_store: AnnotationStore, ann_type: AnnotationType):
        ann_group = get_annotation_group_type(ann_type)
        anns = []

        logger.info(f"Converting annotations of type '{ann_type.value}' to dict.")
        for ann in ann_store:
            ann_data = {}
            for data in ann:
                k, v = data.key().id(), data.value().get()
                if k != ann_group.value:
                    ann_data[k] = v
            curr_ann = {
                "id": ann.id(),
                "span": {
                    "start": ann.offset().begin().value(),
                    "end": ann.offset().end().value(),
                },
                **ann_data,
            }

            anns.append(curr_ann)

        logger.info(
            f"Converted {len(anns)} annotations to dict for type '{ann_type.value}'."
        )
        return anns

    @staticmethod
    def _get_ann_type(layer_path: str):
        layer_name = layer_path.split("/")[1]
        ann_name = layer_name.split("-")[0]
        return get_annotation_type(ann_name)

    def get_edition_base(self, pecha: Pecha, edition_layer_path: str) -> str:
        """
        1.Get base from Pecha.
        2.Read Spelling Variant Annotations from Edition Layer path
        3.Form a new base for Edition
        """
        ann_store = AnnotationStore(file=str(pecha.layer_path / edition_layer_path))
        ann_type = self._get_ann_type(edition_layer_path)
        anns = self.to_dict(ann_store, ann_type)

        old_base = self.get_base(pecha)
        edition_base = ""

        cursor = 0
        for ann in anns:
            start, end = ann["span"]["start"], ann["span"]["end"]
            operation, text = ann["operation"], ann["text"]

            edition_base += old_base[cursor:start]

            if operation == VersionVariantOperations.INSERTION:
                edition_base += text
            elif operation == VersionVariantOperations.DELETION:
                pass  # Skip deleted text
            else:
                raise ValueError(
                    f"Invalid operation: {operation}. Expected 'insertion' or 'deletion'."
                )

            cursor = end

        logger.info("Successfully constructed edition base.")
        return edition_base

    def get_annotation_paths(self, pecha: Pecha, annotations: list[dict]):
        version_annotation_path = None

        def get_annotation_names(annotations: list[dict]):
            version_annotation = None
            annotation_filenames = []
            for annotation in annotations:
                if annotation['type'] == 'version':
                    version_annotation = annotation['type'] + "-" + annotation["id"]
                elif annotation['type'] == 'alignment':
                    continue
                else:
                    filename = annotation['type'] + "-" + annotation["id"]
                    annotation_filenames.append(filename)
            return version_annotation, annotation_filenames
        
        annotation_paths = []
        version_annotation, annotation_filenames = get_annotation_names(annotations)
        for base_name in pecha.bases.keys():
            for path in Path(pecha.layer_path/base_name).iterdir():
                if path.stem in annotation_filenames:
                    annotation_paths.append("/".join(path.parts[-2:]))
                if version_annotation != None and path.stem in version_annotation:
                    version_annotation_path = "/".join(path.parts[-2:])

        return version_annotation_path, annotation_paths

    def serialize(self, pecha: Pecha, annotations: list[dict] = None) -> PechaJson:
        """
        Get annotations for a single or list of layer paths.
        Each layer_path is a string like: "B5FE/segmentation-4FD1.json"
        """
        
        version_annotation_path, annotation_paths = self.get_annotation_paths(pecha, annotations)
        
        if version_annotation_path != None:
            base = self.get_edition_base(pecha, version_annotation_path) 
        else:
            base = self.get_base(pecha)

        annotations = self.get_annotations(pecha, annotation_paths)

        logger.info(f"Serialization complete for Pecha '{pecha.id}'.")
        return PechaJson(base=base, annotations=annotations)


    def serialize_edition_annotations(
        self, pecha: Pecha, edition_layer_path: str, layer_path: str
    ):
        """
        Get annotations for a single or list of edition layer paths.
        Edition annotations are annotations done on top of edition base rather than the base.
        """
        logger.info(
            f"Serializing edition annotations from layer '{layer_path}' based on edition layer '{edition_layer_path}'."
        )
        edition_base = self.get_edition_base(pecha, edition_layer_path)
        edition_basename = Path(edition_layer_path).stem
        output_path = str(Path(tempfile.mkdtemp()) / pecha.id)

        shutil.copytree(pecha.pecha_path.as_posix(), output_path)
        Path(f"{output_path}/base/{edition_basename}.txt").write_text(
            edition_base, encoding="utf-8"
        )
        temp_pecha = pecha.from_path(Path(output_path))

        serialized = self.serialize(temp_pecha, layer_path)
        logger.info(
            f"Successfully serialized edition annotations for layer '{layer_path}'."
        )
        return serialized

    def get_base_from_pecha(self, pecha: Pecha, annotations: list[dict]):
        version_annotation_path, _ = self.get_annotation_paths(pecha, annotations)
        if version_annotation_path != None:
            base = self.get_edition_base(pecha, version_annotation_path) 
        else:
            base = self.get_base(pecha)
        return base
    

class AlignedPechaJsonSerializer(JsonSerializer):
    """
    Serializer for aligned pechas.
    """
    def __init__(self, target_pecha: Pecha, target_annotations: list[dict], source_pecha: Pecha, source_annotations: list[dict]):
        self.target_pecha = target_pecha
        self.target_annotations = target_annotations
        self.source_pecha = source_pecha
        self.source_annotations = source_annotations

    def get_annotation(self, pecha: Pecha, annotation_paths: list[str], annotation_id: str):
        annotations = {}
        for annotation_path in annotation_paths:
            ann_store = AnnotationStore(file=str(pecha.layer_path / annotation_path))
            ann_type = self._get_ann_type(annotation_path)
            ann_id = annotation_path.split("/")[1][(len(ann_type.value)+1):-5]
            if ann_id == annotation_id:
                annotations[ann_type.value] = self.to_dict(ann_store, ann_type)
                return annotations
        raise ValueError(f"Annotation with id {annotation_id} not found")

    def get_annotation_paths(self, pecha: Pecha, annotations: list[dict]):
        version_annotation_path = None

        def get_annotation_names(annotations: list[dict]):
            version_annotation = None
            annotation_filenames = []
            for annotation in annotations:
                if annotation['type'] == 'version':
                    version_annotation = annotation['type'] + "-" + annotation["id"]
                else:
                    filename = annotation['type'] + "-" + annotation["id"]
                    annotation_filenames.append(filename)
            return version_annotation, annotation_filenames
        
        annotation_paths = []
        version_annotation, annotation_filenames = get_annotation_names(annotations)
        for base_name in pecha.bases.keys():
            for path in Path(pecha.layer_path/base_name).iterdir():
                if path.stem in annotation_filenames:
                    annotation_paths.append("/".join(path.parts[-2:]))
                if version_annotation != None and path.stem in version_annotation:
                    version_annotation_path = "/".join(path.parts[-2:])

        return version_annotation_path, annotation_paths

    def serialize(self) -> AlignedPechaJson:
        source_base = JsonSerializer().get_base_from_pecha(self.source_pecha, self.source_annotations)
        target_base = JsonSerializer().get_base_from_pecha(self.target_pecha, self.target_annotations)
        # transformed_annotation = { "target_annotations": {}, "source_annotations": {} }
        transformed_annotation = self.serialize_aligned_pechas_transformed_annotations()
        untransformed_annotation = self.serialize_aligned_pechas_untransformed_annotations()
        return AlignedPechaJson(
            source_base=source_base,
            target_base=target_base,
            annotation_transformed=transformed_annotation,
            annotation_untransformed=untransformed_annotation
        )
    

    def get_aligned_to_annotation_id(self, annotations: list[dict]):
        for annotation in annotations:
            if annotation['type'] == 'alignment':
                if 'aligned_to' in annotation:
                    target_annotation_id = annotation['aligned_to']
                    source_annotation_id = annotation['id']
                    return target_annotation_id, source_annotation_id
        raise ValueError("No aligned_to annotation found")
    

    def serialize_aligned_pechas_untransformed_annotations(self):
        _, target_annotation_paths = self.get_annotation_paths(self.target_pecha, self.target_annotations)
        _, source_annotation_paths = self.get_annotation_paths(self.source_pecha, self.source_annotations)

        target_annotation_id, source_annotation_id = self.get_aligned_to_annotation_id(self.source_annotations)
        target_annotation = self.get_annotation(self.target_pecha, target_annotation_paths, target_annotation_id)
        source_annotation = self.get_annotation(self.source_pecha, source_annotation_paths, source_annotation_id)
        
        return { "target_annotation": target_annotation, "source_annotation": source_annotation }
    

    def get_segmentation_annotation_store(self, pecha: Pecha, annotation_paths: list[str]):
        for annotation_path in annotation_paths:
            ann_store = AnnotationStore(file=str(pecha.layer_path / annotation_path))
            ann_type = self._get_ann_type(annotation_path)
            if ann_type.value == 'segmentation':
                return ann_store
        raise ValueError("No segmentation annotation found")


    # def get_transformed_annotation(self, pecha: Pecha, annotation_paths: list[str], annotation_id: str):
    #     annotations = []
    #     for annotation_path in annotation_paths:
    #         ann_store = AnnotationStore(file=str(pecha.layer_path / annotation_path))
    #         ann_type = self._get_ann_type(annotation_path)
    #         ann_id = annotation_path.split("/")[1][(len(ann_type.value)+1):-5]
    #         if ann_id == annotation_id and ann_type.value == 'segmentation':
    #             return self.to_dict(ann_store, ann_type)
    #         elif ann_id == annotation_id and ann_type.value == 'alignment':
    #             src_ann_store = AnnotationStore(file=str(self.source_pecha.layer_path / annotation_path))
    #             tgt_ann_store = self.get_segmentation_annotation_store(self.target_pecha, annotation_paths)
    #     raise ValueError(f"Annotation with id {annotation_id} not found")

    

    def serialize_aligned_pechas_transformed_annotations(self):
        target_annotation_id, source_annotation_id = self.get_aligned_to_annotation_id(self.source_annotations)
        _, target_annotation_paths = self.get_annotation_paths(self.target_pecha, self.target_annotations)
        _, source_annotation_paths = self.get_annotation_paths(self.source_pecha, self.source_annotations)

        target_annotation_id, source_annotation_id = self.get_aligned_to_annotation_id(self.source_annotations)
        
        is_target_annnotation_is_alignement = self._check_if_target_annotation_is_alignment_(self.target_annotations)

        target_alignment_annotation = None
        if is_target_annnotation_is_alignement:
            target_alignment_annotation_id = target_annotation_id
            target_alignment_annotation = self.get_annotation(self.target_pecha, target_annotation_paths, target_alignment_annotation_id)

        target_segmentatation_annotation_id = self._get_target_segmentation_annotation_id_(self.target_annotations)
        
        target_segmentation_annotation = self.get_annotation(self.target_pecha, target_annotation_paths, target_segmentatation_annotation_id)

        mapped_compare_annotation = TranslationAlignmentMapping().map_annotation_layer_to_layer(target_segmentation_annotation, target_alignment_annotation)

        source_alignment_annotation = self.get_annotation(self.source_pecha, source_annotation_paths, source_annotation_id)
        
        source_annotation = self._updated_source_annotation_base_on_mapped_compare_annotation_(source_alignment_annotation, mapped_compare_annotation)

        return { "target_annotations": target_segmentation_annotation, "source_annotations": source_annotation }
    
    def _updated_source_annotation_base_on_mapped_compare_annotation_(self, source_alignment_annotation: dict, mapped_compare_annotation: dict) -> dict:
        if mapped_compare_annotation == {}:
            return source_alignment_annotation
        
        for source_annotation in source_alignment_annotation['alignment']:
            new_alignment_index = []
            for alignment_index in source_annotation['alignment_index']:
                if alignment_index in mapped_compare_annotation:
                    new_alignment_index.extend(mapped_compare_annotation[alignment_index])

            new_alignment_index = list(set(new_alignment_index))
            
            source_annotation['alignment_index'] = new_alignment_index

        return source_alignment_annotation
            
    
    def _get_target_segmentation_annotation_id_(self, target_annotations: list[dict]) -> str:
        for target_annotation in target_annotations:
            if (target_annotation['type'] == 'segmentation'):
                return target_annotation['id']
        raise ValueError("No segmentation annotation found")

    def _check_if_target_annotation_is_alignment_(self, target_annotations: list[dict]) -> bool:
        for target_annotation in target_annotations:
            if (target_annotation['type'] == 'alignment'):
                return True
        return False
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from stam import AnnotationStore, Offset, Selector

from openpecha.exceptions import StamAddAnnotationError
from openpecha.ids import (
    get_annotation_id,
    get_base_id,
    get_initial_pecha_id,
    get_layer_id,
)
from openpecha.pecha.annotations import BaseAnnotation
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.metadata import PechaMetaData
from openpecha.config import PECHAS_PATH

BASE_NAME = str
annotation_path = str


class Pecha:
    def __init__(self, pecha_id: str, pecha_path: Path) -> None:
        self.id = pecha_id
        self.pecha_path = pecha_path
        self.metadata = self.load_metadata()
        self.bases = self.load_bases()

    @classmethod
    def from_path(cls, pecha_path: Path) -> "Pecha":
        pecha_id = pecha_path.stem
        return cls(pecha_id, pecha_path)

    @classmethod  
    def create(cls, output_path: Optional[Path] = None, pecha_id: Optional[str] = None) -> "Pecha":
        if pecha_id is None:
            pecha_id = get_initial_pecha_id()
        
        if output_path is None:
            output_path = PECHAS_PATH
            
        pecha_path = output_path / pecha_id
        if pecha_path.exists():
            shutil.rmtree(pecha_path)
        pecha_path.mkdir(parents=True, exist_ok=True)
        return cls(pecha_id, pecha_path)
    
    @classmethod
    def create_pecha(cls, pecha_id: str, base_text: str, annotation_id: str, annotation: List[BaseAnnotation]) -> "Pecha":
        pecha = cls.create(pecha_id=pecha_id)
        base_name = pecha.set_base(base_text)
        ann_type = get_annotation_type(annotation)
        ann_store, _ = pecha.add_layer(base_name=base_name, layer_type=ann_type, annotation_id=annotation_id)
        
        for single_annotation in annotation:
            ann_store = pecha.add_annotation(ann_store=ann_store, annotation=single_annotation, layer_type=ann_type)
            ann_store.save()
        return pecha
    
    
    def add(self, annotation_id: str, annotation: List[BaseAnnotation]) -> "Pecha":
        base_name = next(iter(self.bases))
        ann_type = get_annotation_type(annotation)
        if check_annotation_exists(self.layer_path/base_name/f"{ann_type.value}-{annotation_id}.json"):
            raise ValueError(f"Annotation with id {annotation_id} already exists")
        ann_store, _ = self.add_layer(base_name=base_name, layer_type=ann_type, annotation_id=annotation_id)
        for single_annotation in annotation:
            ann_store = self.add_annotation(ann_store=ann_store, annotation=single_annotation, layer_type=ann_type)
            ann_store.save()
        return annotation_id

    @property
    def base_path(self) -> Path:
        base_path = self.pecha_path / "base"
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    @property
    def layer_path(self):
        layer_path = self.pecha_path / "layers"
        if not layer_path.exists():
            layer_path.mkdir(parents=True, exist_ok=True)
        return layer_path

    @property
    def metadata_path(self):
        return self.pecha_path / "metadata.json"
        

    def load_metadata(self):
        if not self.metadata_path.exists():
            return None

        with open(self.metadata_path) as f:
            metadata = json.load(f)

        return PechaMetaData(**metadata)

    def load_bases(self):
        bases = {}
        for base_file in self.base_path.rglob("*.txt"):
            base_name = base_file.stem
            bases[base_name] = base_file.read_text(encoding="utf-8")
        return bases

    def get_base(self, base_name) -> str:
        return (self.base_path / f"{base_name}.txt").read_text()

    def set_base(self, content: str, base_name=None):
        base_name = base_name if base_name else get_base_id()
        (self.base_path / f"{base_name}.txt").write_text(content)

        # add base to the attribute 'bases'
        if base_name not in self.bases:
            self.bases[base_name] = content

        # make a folder for the base in the 'layers' folder
        (self.layer_path / base_name).mkdir(parents=True, exist_ok=True)
        return base_name

    def add_layer(self, base_name: str, layer_type: AnnotationType, annotation_id: str = None):
        """
        Inputs:
            base_name: .txt file which this annotation is associated with
            layer_type: the type of annotation layer, it should be include in AnnotationType

        Process:
            - create an annotation store
            - add the resource to the annotation store
            - add the dataset to the annotation store

        Output:
            - annotation store
        """
        if base_name not in self.bases:
            raise ValueError(f"Base {base_name} does not exist.")

        if annotation_id is None:
            annotation_id = get_layer_id()

        ann_store = AnnotationStore(id=annotation_id)
        ann_store_path = (
            self.layer_path / base_name / f"{layer_type.value}-{annotation_id}.json"
        )
        ann_store.set_filename(str(ann_store_path))
        ann_store.add_resource(
            id=base_name,
            filename=f"../../base/{base_name}.txt",
        )
        dataset_id = layer_type.annotation_collection_type._value_
        ann_store.add_dataset(id=dataset_id)

        return ann_store, ann_store_path

    def add_annotation(
        self,
        ann_store: AnnotationStore,
        annotation: BaseAnnotation,
        layer_type: AnnotationType,
    ) -> AnnotationStore:
        """
        Adds an annotation to an Existing Annotation Layer(Annotation Store)
        """

        ann_resource = next(ann_store.resources())
        ann_dataset = next(ann_store.datasets())

        ann_data: Dict = annotation.get_dict()
        # Add Annotation Group Type
        ann_group_type = layer_type.annotation_group_type
        ann_data[ann_group_type.value] = layer_type.value

        start, end = (
            annotation.span.start,
            annotation.span.end,
        )
        text_selector = Selector.textselector(ann_resource, Offset.simple(start, end))

        # If ann data already exists, use it . Otherwise create a new one with new id
        prepared_ann_data = []
        for k, v in ann_data.items():
            try:
                ann_datas = list(ann_store.data(set=ann_dataset.id(), key=k, value=v))
                prepared_ann_data.append(ann_datas[0])
            except:  # noqa
                prepared_ann_data.append(
                    {
                        "id": get_annotation_id(),
                        "set": ann_dataset.id(),
                        "key": k,
                        "value": v,
                    }
                )
        try:
            ann_store.annotate(
                target=text_selector, data=prepared_ann_data, id=get_annotation_id()
            )
        except Exception as e:
            raise StamAddAnnotationError(
                f"[Error] Failed to add annotation to STAM: {e}"
            )
        return ann_store

    def set_metadata(self, pecha_metadata: Dict):
        # Retrieve parser name
        parser_name = self.metadata.parser if self.metadata else None
        if "parser" not in pecha_metadata:
            pecha_metadata["parser"] = parser_name

        # Retrieve initial creation type name
        initial_creation_type = (
            self.metadata.initial_creation_type if self.metadata else None
        )
        if "initial_creation_type" not in pecha_metadata:
            pecha_metadata["initial_creation_type"] = initial_creation_type

        try:
            pecha_metadata = PechaMetaData(**pecha_metadata)
        except Exception as e:
            raise ValueError(f"Invalid metadata: {e}")

        self.metadata = pecha_metadata
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata.to_dict(), f, ensure_ascii=False, indent=2)

        return self.metadata

    def get_segmentation_layer_path(self) -> str:
        """
        1. Get the first layer file from the pecha
        2. Get the relative path of the layer file
        TODO: Modify this function in future in case of more layers in a Pecha
        """
        layer_path = list(self.layer_path.rglob("segmentation-*.json"))[0]
        relative_layer_path = layer_path.relative_to(self.pecha_path.parent).as_posix()

        return relative_layer_path

    def get_first_layer_path(self) -> str:
        layer_path = list(self.layer_path.rglob("*.json"))[0]
        relative_layer_path = layer_path.relative_to(self.pecha_path.parent).as_posix()

        return relative_layer_path

    def get_layer_by_ann_type(self, base_name: str, layer_type: AnnotationType):
        """
        Get layers by annotation type i.e Chapter, Sabche, Segment,...
        """
        dir_to_search = self.layer_path / base_name
        ann_store_files = list(dir_to_search.glob(f"{layer_type.value}*.json"))

        annotation_stores = [
            AnnotationStore(file=str(annotation_file))
            for annotation_file in ann_store_files
        ]

        if len(annotation_stores) == 1:
            return annotation_stores[0], ann_store_files[0]
        return annotation_stores, ann_store_files


def get_anns(ann_store: AnnotationStore, include_span: bool = False):
    anns = []
    for ann in ann_store:
        ann_data = {}
        for data in ann:
            ann_data[data.key().id()] = data.value().get()
        curr_ann = {**ann_data, "text": str(ann)}
        if include_span:
            curr_ann["span"] = {
                "start": ann.offset().begin().value(),
                "end": ann.offset().end().value(),
            }
        anns.append(curr_ann)
    return anns   


def load_layer(path: Path) -> AnnotationStore:
    return AnnotationStore(file=str(path))


def get_annotation_type(annotation: List[BaseAnnotation]):
    if hasattr(annotation[0], "alignment_index") and hasattr(annotation[0], "index"):
        return AnnotationType.ALIGNMENT
    elif hasattr(annotation[0], "index") and not hasattr(annotation[0], "alignment_index"):
        return AnnotationType.SEGMENTATION
    else:
        raise ValueError("Invalid annotation type")

def check_annotation_exists(annotation_path: Path):
    if annotation_path.exists():
        return True
    return False
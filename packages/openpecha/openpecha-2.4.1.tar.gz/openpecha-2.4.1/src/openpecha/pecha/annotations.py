import json
import re
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    field_validator,
    model_validator,
)
from pydantic_core import core_schema

from openpecha.ids import get_uuid
from openpecha.pecha.layer import AnnotationType


class span(BaseModel):
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    errors: Optional[Dict] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("start", "end")
    @classmethod
    def span_must_not_be_neg(cls, v: int) -> int:
        if v < 0:
            raise ValueError("span shouldn't be negative")
        return v

    @model_validator(mode="after")
    def end_must_not_be_less_than_start(self) -> "span":
        if self.end < self.start:
            raise ValueError("Span end must not be less than start")
        return self


class BaseAnnotation(BaseModel):
    span: span
    metadata: Optional[Dict] = None

    model_config = ConfigDict(extra="allow")

    def get_dict(self):
        res = self.model_dump()
        # Remove span from the dictionary
        res.pop("span")
        # Remove None values from the dictionary
        res = {k: v for k, v in res.items() if v is not None}
        return res


class SegmentationAnnotation(BaseAnnotation):
    index: int


class AlignmentAnnotation(BaseAnnotation):
    index: int
    alignment_index: list[int] = Field(
        description="Index of the alignment, which can be of translation or commentary"
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"index": 5, "alignment_index": [1, 3, 4]}}
    )


class VersionVariantOperations(str, Enum):
    INSERTION = "insertion"
    DELETION = "deletion"


class Version(BaseAnnotation):
    span: span
    operation: VersionVariantOperations
    text: str = ""  # Required for insertion, empty for deletion


class FootnoteAnnotation(BaseAnnotation):
    index: int
    note: str


class PedurmaAnnotation(BaseAnnotation):
    note: str


class SapcheAnnotation(BaseAnnotation):
    sapche_number: str


class Page(BaseAnnotation):
    page_info: Optional[str] = Field(default=None, description="page payload")
    imgnum: Optional[int] = Field(
        default=None,
        description="image sequence no. from bdrc api, http://iiifpres.bdrc.io/il/v:bdr:I0888",
    )
    reference: Optional[str] = Field(
        default=None, description="image filename from bdrc"
    )


class Pagination(BaseAnnotation):
    page_info: Optional[str] = Field(default=None, description="page payload")
    imgnum: Optional[int] = Field(default=None, description="image sequence number")
    order: Optional[int] = Field(default=None, description="order of the page")
    reference: Optional[str] = Field(
        default=None, description="can be url or just string indentifier of source page"
    )


class Lang(BaseAnnotation):
    language: Optional[str] = Field(
        default=None, description="BCP-47 tag of the language"
    )


class OCRConfidence(BaseAnnotation):
    confidence: float
    nb_below_threshold: Optional[int] = None


class Citation(BaseAnnotation):
    pass


def _get_annotation_class(layer_name: AnnotationType):
    """Maps AnnotationType to Annotation class"""

    if layer_name == AnnotationType.PAGINATION:
        return Pagination
    elif layer_name == AnnotationType.LANGUAGE:
        return Lang
    elif layer_name == AnnotationType.CITATION:
        return Citation
    elif layer_name == AnnotationType.OCR_CONFIDENCE:
        return OCRConfidence
    else:
        return BaseAnnotation


class Layer(BaseModel):
    id: str = Field(default=None)
    annotation_type: AnnotationType
    revision: str = Field(default="00001")
    annotations: Dict = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    def set_id(cls, values):
        values["id"] = values.get("id") or get_uuid()
        return values

    @field_validator("revision")
    def revision_must_int_parsible(cls, v):
        if not v.isdigit():
            raise ValueError("revision must be integer-parsable like `00002`")
        return v

    def bump_revision(self):
        self.revision = f"{int(self.revision)+1:05}"  # noqa

    def reset(self):
        self.revision = "00001"
        self.annotations = {}

    def get_annotations(self):
        """Yield Annotation Objects"""
        for ann_id, ann_dict in self.annotations.items():
            ann_class = _get_annotation_class(self.annotation_type)
            ann = ann_class.model_validate(ann_dict)
            yield ann_id, ann

    def get_annotation(self, annotation_id: str) -> Optional[BaseAnnotation]:
        """Retrieve annotation of id `annotation_id`"""
        ann_dict = self.annotations.get(annotation_id)
        if not ann_dict:
            return None
        ann_class = _get_annotation_class(self.annotation_type)
        ann = ann_class.model_validate(ann_dict)
        return ann

    def set_annotation(self, ann: BaseAnnotation, ann_id=None):
        """Add or Update annotation `ann` to the layer, returns the annotation id"""
        ann_id = ann_id if ann_id is not None else get_uuid()
        self.annotations[ann_id] = json.loads(ann.model_dump_json())
        return ann_id

    def remove_annotation(self, annotation_id: str):
        """Delete annotaiton of `annotation_id` from the layer"""
        if annotation_id in self.annotations:
            del self.annotations[annotation_id]


class OCRConfidenceLayer(Layer):
    confidence_threshold: float
    annotation_type: AnnotationType = Field(default=AnnotationType.OCR_CONFIDENCE)


class PechaId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate, core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v, info=None):  # <-- add info=None
        if not re.fullmatch(r"^I[A-F0-9]{8}$", v):
            raise ValueError(
                "PechaId must start with 'I' followed by 8 uppercase hex characters"
            )
        return v


class PechaAlignment(BaseModel):
    pecha_id: PechaId = Field(..., description="Pecha ID")
    alignment_id: Optional[str] = Field(
        default=None, pattern="\\S", description="Alignment ID"
    )


class AnnotationModel(BaseModel):
    pecha_id: PechaId = Field(..., description="Pecha ID")
    type: AnnotationType = Field(
        AnnotationType.SEGMENTATION, description="Type of the annotation"
    )
    document_id: str = Field(..., pattern="\\S")
    path: str = Field(..., pattern="\\S")
    title: str = Field(..., min_length=1)
    aligned_to: PechaAlignment | None = Field(None, description="Alignment descriptor")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": {
                "pecha_id": "I857977C3",
                "type": "alignment",
                "document_id": "1vgnfCQH3yaWPDaMDFXT_5GhlG0M9kEra0mxkDX46VLE",
                "annotation_id": "test_id",
                "title": "Test Alignment",
                "aligned_to": {
                    "pecha_id": "I857977C3",
                    "alignment_id": "test_alignment_id",
                },
            }
        },
    )

class PechaJson(BaseModel):
    base: str = Field(..., description="Base text content")
    annotations: Dict[str, Any] = Field(..., description="Annotations dictionary")
    
    model_config = ConfigDict(extra="forbid")

class AlignedPechaJson(BaseModel):
    source_base: str = Field(..., description="Source base text content")
    target_base: str = Field(..., description="Target base text content")
    annotation_transformed: Dict[str, Dict[str, Any]] = Field(..., description="Transformed annotations")
    annotation_untransformed: Dict[str, Dict[str, Any]] = Field(..., description="Untransformed annotations")
    
    model_config = ConfigDict(extra="forbid")
    
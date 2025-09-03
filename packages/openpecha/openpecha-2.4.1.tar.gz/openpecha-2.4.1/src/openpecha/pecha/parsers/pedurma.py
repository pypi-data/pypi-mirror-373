import re
from pathlib import Path
from typing import Dict, List

from botok.tokenizers.chunktokenizer import ChunkTokenizer

from openpecha.config import PECHAS_PATH
from openpecha.pecha import Pecha
from openpecha.pecha.annotations import PedurmaAnnotation, SegmentationAnnotation, span
from openpecha.pecha.layer import AnnotationType
from openpecha.pecha.parsers import BaseParser
from openpecha.utils import read_json


class PedurmaParser(BaseParser):
    def __init__(self):
        self.ann_regex = r"(\(\d+\) <.+?>)"
        self.pagination_regex = r"\d+-\d+"
        self.base_text = ""
        self.pedurma_anns = []
        self.meaning_segment_anns = []

    def get_base_text(self, text: str):
        text = re.sub(self.ann_regex, "", text)
        text = text.replace(":", "")
        return text

    def parse(
        self,
        input: str,
        metadata: Dict | Path,
        output_path: Path = PECHAS_PATH,
    ) -> Pecha:

        # Remove pagination
        input = re.sub(self.pagination_regex, "", input)
        self.base_text = self.get_base_text(input)

        # Normalize newlines with #
        input = input.replace("\n", "#")
        char_walker = 0
        # Split the text into chunks with anns regex
        chunks = re.split(self.ann_regex, input)
        prev_chunk = chunks[0]
        self.pedurma_anns = []
        for chunk in chunks:
            if re.search(self.ann_regex, chunk):
                ann = get_annotation(prev_chunk, chunk, char_walker)
                self.pedurma_anns.append(ann)
            else:
                clean_chunk = chunk.replace(":", "")
                char_walker += len(clean_chunk)
            prev_chunk = chunk

        input = input.replace("#", "\n")

        # Segment Annotation
        char_walker = 0
        self.meaning_segment_anns = []
        for index, line in enumerate(self.base_text.splitlines()):
            segment_ann = SegmentationAnnotation(
                span=span(start=char_walker, end=char_walker + len(line)), index=index
            )
            self.meaning_segment_anns.append(segment_ann)
            char_walker += len(line)
            char_walker += 1  # Add because of new line

        # Create a pecha
        pecha = Pecha.create(output_path)

        basename = pecha.set_base(self.base_text)

        # Add Durchen Layer
        durchen_layer, _ = pecha.add_layer(basename, AnnotationType.DURCHEN)
        for ann in self.pedurma_anns:
            pecha.add_annotation(durchen_layer, ann, AnnotationType.DURCHEN)

        durchen_layer.save()

        # Add Segment Layer
        segment_layer, _ = pecha.add_layer(basename, AnnotationType.SEGMENTATION)
        for ann in self.meaning_segment_anns:
            pecha.add_annotation(segment_layer, ann, AnnotationType.SEGMENTATION)

        segment_layer.save()
        # Set metadata
        if isinstance(metadata, Path):
            metadata = read_json(metadata)

        assert isinstance(metadata, dict)
        metadata = modify_metadata(metadata)
        pecha.set_metadata({"id": pecha.id, "parser": self.name, **metadata})  # noqa

        return pecha


def modify_metadata(metadata: Dict) -> Dict:
    modified_metadata = {
        k: v
        for k, v in metadata.items()
        if k not in ["title_bo", "alt_title_bo", "author_en", "author_bo"]
    }
    modified_metadata["title"] = {
        "title_bo": metadata["title_bo"],
        "alt_title_bo": metadata["alt_title_bo"],
    }
    modified_metadata["author"] = {
        "author_en": metadata["author_en"],
        "author_bo": metadata["author_bo"],
    }
    return modified_metadata


def get_annotation(
    prev_chunk: str, note_chunk: str, char_walker: int
) -> PedurmaAnnotation:
    span_text = get_span_text(prev_chunk, note_chunk)
    start = char_walker - len(span_text)
    end = char_walker

    return PedurmaAnnotation(span=span(start=start, end=end), note=note_chunk)


def get_span_text(prev_chunk: str, note_chunk: str):
    """
    Input: text chunk
    Process: Extract span text where the syllable/words have variations
             if ':' is present, extract the text after ':'
             else extract the last syllable
    Output: span text

    Example:
    Input: །དེ་བཞིན་ཉོན་མོངས་རྣམ་  Output: རྣམ་
    Input: ཆོས་ཀྱི་དབྱིངས་སུ་བསྟོད་པ། :འཕགས་པ་འཇམ་ Output: འཕགས་པ་འཇམ་
    """
    span_text = ""
    if "+" in note_chunk:
        return span_text
    if ":" in prev_chunk:
        match = re.search(":.*", prev_chunk)
        if match:
            span_text = match.group(
                0
            )  # Use group(0) to safely access the matched string
    else:
        syls = get_syls(prev_chunk)
        if syls:
            span_text = syls[-1]
            if span_text == "#":
                span_text = syls[-2]
    span_text = span_text.replace("#", "\n")
    span_text = span_text.replace(":", "")
    return span_text


def get_syls(text: str):
    """
    Split the text into syllables
    """
    tokenizer = ChunkTokenizer(text)

    tokens = tokenizer.tokenize()
    syls: List = []
    syl_walker = 0
    for token in tokens:
        token_string = token[1]
        if is_shad(token_string):
            try:
                syls[syl_walker - 1] += token_string
            except:  # noqa
                syls.append(token_string)
                syl_walker += 1
        else:
            syls.append(token_string)
            syl_walker += 1
    return syls


def is_shad(text):
    shads = ["། །", "།", "།།", "། "]
    if text in shads:
        return True
    return False


"""
PEDURMA PREPROCESSING
"""


def filter_pedurma_ann(text: str):
    # remove <«སྣར་»«པེ་»བསྒྲུབ་པའི་> from text
    text = re.sub(r"<[\u0F00-\u0FFF\s«»]+>", "", text)
    # remove numbering (28) from text
    text = re.sub(r"\(\d+\)", "", text)

    return text


def split_by_shad(text: str):
    return text.split("།")


def preprocess_pedurma_text(text: str):
    from bo_sent_tokenizer import segment
    from fast_antx.core import transfer

    filtered_text = filter_pedurma_ann(text)
    tokenized_text = segment(filtered_text, keep_non_bo_and_symbols=True)

    annotations = [["note_transfer", r"(\(\d+\) <[\u0F00-\u0FFF\s«»]+>)"]]
    preprocessed_text = transfer(text, annotations, tokenized_text, output="txt")

    return preprocessed_text
